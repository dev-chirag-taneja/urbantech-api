from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout

from .serializers import *


# Register View
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer


# Change Password View
class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        """The get_object function is necessary to retrieve the specific User instance that is currently logged in and making the request. This ensures that the password change operation is performed on the correct user."""
        return self.request.user


# Activate User View
class ActivateUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ActivateUserSerializer

    def get_serializer_context(self):
        return {"pk": self.kwargs["pk"], "otp": self.kwargs["otp"]}


# Resend Activation Email View
class ResendActivationEmailView(generics.CreateAPIView):
    serializer_class = ResendActivationEmailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request)
        return Response(
            {"detail": "Activation link has been sent to your email."}, status=200
        )


# Password Reset View
class PasswordResetRequestView(generics.CreateAPIView):
    serializer_class = PasswordResetRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password reset link has been sent to your email."}, status=200
        )


# Password Reset Confirm View
class PasswordResetConfirmView(generics.CreateAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password has been reset successfully."}, status=200)


# List Profile View
class ListUserView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    cache_timeout = 120

    def get_queryset(self):
        cache_key = "user_list"
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = Profile.objects.all()
            cache.set(cache_key, queryset, timeout=self.cache_timeout)
        return queryset


# Profile View
class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


# Delete Profile View
class DeleteUserView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, pk):
        user = get_object_or_404(Profile, id=pk)
        user.delete()
        return Response({"message": "Profile Deleted!"})
