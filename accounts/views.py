from rest_framework.response import Response
from rest_framework import generics 
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from rest_framework import status
from django.contrib.auth.forms import PasswordResetForm

from .serializers import *


# Register Api
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer


# Login Api
class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    
    # def post(self, request):
    #     serializer = self.serializer_class(data=request.data)
    #     print(serializer)
    #     serializer.is_valid(raise_exception=True)
    #     print(serializer.data)
    #     user = User.objects.get(email=serializer.validated_data["email"])
    #     token, _ = Token.objects.get_or_create(user=user)
    #     return Response({
    #         'message': 'User Logged in!',
    #         'email': user.email,
    #         'token': str(token)})


# Logout Api
class LogoutView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        request.user.auth_token.delete()
        logout(request)
        return Response({'message': 'User Logged out successfully!'})


# Change Password Api
class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer 
    
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        # make sure to catch 404's below
        obj = queryset.get(pk=self.request.user.id)
        self.check_object_permissions(self.request, obj)
        return obj


# Activate User By Token 
class ActivateUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ActivateUserSerializer
    
    def get_serializer_context(self):
        return {'pk' : self.kwargs['pk'], 'otp': self.kwargs['otp']}


# Reset Password
class PasswordResetView(generics.CreateAPIView):
    # queryset = User.objects.all()
    serializer_class = PasswordResetSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"message": "No account with this email address."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate and send the password reset email
            form = PasswordResetForm(data={"email": email})
            if form.is_valid():
                form.save(request=self.request)
                return Response(
                    {"message": "Password reset email sent."},
                    status=status.HTTP_200_OK
                )
            else:
                raise serializer.ValidationError("An error occurred while sending the password reset email.")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# List Profile Api
class ListUserView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    
# Profile Api
class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    # https://stackoverflow.com/questions/43859053/django-rest-framework-assertionerror-fix-your-url-conf-or-set-the-lookup-fi
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(user=self.request.user)
        self.check_object_permissions(self.request, obj)
        return obj
    
    # def put(self, request):
    #     profile = get_object_or_404(Profile, user=request.user)         
    #     serializer = ProfileSerializer(profile, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED) 
    
    
# Delete Profile Api
class DeleteUserView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def delete(self, request, pk):
        user = get_object_or_404(Profile, id=pk)
        user.delete()
        return Response({'message': 'Profile Deleted!'})