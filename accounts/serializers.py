from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

from .models import *
from order.models import Address
from .tasks import send_mail_link


# Register Serializer
class RegistrationSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(max_length=255, required=True)
    last_name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all(), message="Email already exist!")
        ],
    )
    password = serializers.CharField(
        required=True, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        required=True, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password", "password2"]

    def validate(self, obj):
        if obj["password"] != obj["password2"]:
            raise ValidationError({"password": "Password mismatch!"})

        return obj

    def create(self, validated_data):
        user = User.objects.create(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


# Change Password Serializer
class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(
        required=True, style={"input_type": "password"}, write_only=True
    )
    password = serializers.CharField(
        required=True, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = ["old_password", "password"]

    def validate(self, obj):
        user = self.context["request"].user
        check_password = user.check_password(obj["old_password"])
        if not check_password:
            raise ValidationError({"old_password": "Password is incorrect!"})
        return obj

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password"])
        instance.save()
        return instance


# Activate User Serializer
class ActivateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["pk", "otp"]

    def validate(self, obj):
        try:
            user = User.objects.get(id=self.context["pk"])
        except Exception as e:
            raise ValidationError({"user": "User not found!", "error": str(e)})

        if user.otp != self.context["otp"]:
            raise ValidationError({"message": "Incorrect Otp!"})

        return obj

    def update(self, instance, validated_data):
        instance.is_active = True
        instance.save()
        return instance


# Resend Activation Email Serializer
class ResendActivationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        if user.is_active:
            raise serializers.ValidationError("This account is already active.")

        return value

    def save(self, request):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        activation_link = request.build_absolute_uri(
            f"/api/auth/activate-user/{user.id}/{user.otp}/"
        )
        send_mail_link.delay(
            "Activate Your Account",
            f"Click the link to activate your account: {activation_link}",
            "noreply@yourdomain.com",
            [user.email],
        )


# Password Reset Serializer
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise ValidationError(
                "This email address is not associated with any account."
            )
        return value

    def save(self):
        request = self.context.get("request")
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = request.build_absolute_uri(
            f"/api/auth/reset-password-confirm/{uid}/{token}/"
        )
        send_mail_link.delay(
            "Password Reset Request",
            f"Click the link to reset your password: {reset_link}",
            "noreply@yourdomain.com",
            [email],
        )


# Password Reset Confirm Serializer
class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(
        required=True, style={"input_type": "password"}, write_only=True
    )

    def validate(self, data):
        try:
            uid = urlsafe_base64_decode(data["uid"]).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValidationError({"uid": "Invalid user ID"})

        if not default_token_generator.check_token(user, data["token"]):
            raise ValidationError({"token": "Invalid or expired token"})

        return data

    def save(self):
        uid = urlsafe_base64_decode(self.validated_data["uid"]).decode()
        user = User.objects.get(pk=uid)
        user.set_password(self.validated_data["new_password"])
        user.save()


# Profile List Serializer
class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "name", "email", "location"]


# Address Serializer
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "address", "zip_code", "city", "state", "country"]


# Profile Serializer
class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=False,
        validators=[
            UniqueValidator(queryset=User.objects.all(), message="Email already exist!")
        ],
    )
    addresses = AddressSerializer(source="user.addresses", many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ["name", "email", "avatar", "location", "addresses"]
