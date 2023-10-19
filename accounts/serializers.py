from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from drf_writable_nested.serializers import WritableNestedModelSerializer

from .models import *
from order.serializers import AddressSerializer


# Register Serializer
class RegistrationSerializer(serializers.ModelSerializer):
    
    first_name = serializers.CharField(max_length=255, required=True)
    last_name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(
                required=True,
                validators=[UniqueValidator(queryset=User.objects.all(), message="Email already exist!")],
            )
    password = serializers.CharField(
                required=True,
                style={"input_type": "password"},
                write_only=True)
    password2 = serializers.CharField(
                required=True,
                style={"input_type": "password"},
                write_only=True)
    
    class Meta:
        model  = User
        fields = ["first_name", "last_name", "email", "password", "password2"]
        
    def validate(self, obj):
        if obj["password"] != obj["password2"]:
            raise serializers.ValidationError({"password":"Password mismatch!"})
        
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
    

# Login Serializer
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
                required=True,
                style={"input_type": "password"},
                write_only=True)

    token = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)

    class Meta:
        model  = User
        fields = ["email", "password", "token", "message"]
    
    def validate(self, obj):
        try:
            user = User.objects.get(email=obj["email"])
        except Exception as e:
            raise serializers.ValidationError({"user":"User not found!", "error":str(e)})

        if not user.check_password(obj["password"]):
            raise serializers.ValidationError({"password": "Incorrect Login Credentials!"})

        if not user.is_active:
            raise serializers.ValidationError({"user": "User is not active!"})

        return obj

    def create(self, validated_data):
        user = User.objects.get(email=validated_data["email"])
        token, _ = Token.objects.get_or_create(user=user)
        data = {"message": "User Logged In!", "email": validated_data["email"], "token": str(token)}
        return data
     
     
# Change Password Serializer
class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(
                required=True,
                style={"input_type": "password"},
                write_only=True)
    password = serializers.CharField(
                required=True,
                style={"input_type": "password"},
                write_only=True)
    
    class Meta:
        model = User
        fields = ["old_password", "password"]

    def validate(self, obj):
        user = self.context['request'].user
        check_password = user.check_password(obj["old_password"])
        if not check_password:
            raise serializers.ValidationError({"old_password":"Password is incorrect!"})
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
            raise serializers.ValidationError({"user":"User not found!", "error":str(e)})

        if user.otp != self.context['otp']:
            raise serializers.ValidationError({"message": "Incorrect Otp!"})

        return obj

    def update(self, instance, validated_data):
        instance.is_active = True
        instance.save()
        return instance


# Password Reset Serializer
class PasswordResetSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    
    class Meta:
        model = User 
        fields = ["email"]

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account with this email address.")
        return value
        
             
# Profile List Serializer
class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "name", "email", "location"]   
     
     
# Profile Serializer
class ProfileSerializer(serializers.ModelSerializer):
    # user = serializers.StringRelatedField(read_only=True)
    email = serializers.EmailField(
                required=False,
                validators=[UniqueValidator(queryset=User.objects.all(), message="Email already exist!")])
                
    class Meta:
        model = Profile
        fields = ["name", "email", "avatar", "location"]