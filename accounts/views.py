from rest_framework.response import Response
from rest_framework import generics 
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout

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
        

# List Profile Api
class ListUserView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


# Delete Profile Api
class DeleteUserView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def delete(self, request, pk):
        user = get_object_or_404(Profile, id=pk)
        user.delete()
        return Response({'message': 'Profile Deleted!'})