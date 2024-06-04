# urls.py
# path('login/', LoginView.as_view()),
# path('logout/', LogoutView.as_view()),


# views.py
# from rest_framework import status


# Login View
# class LoginView(generics.CreateAPIView):
#     serializer_class = LoginSerializer

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


# Logout View
# class LogoutView(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         request.user.auth_token.delete()
#         logout(request)
#         return Response({"message": "User Logged out successfully!"})


# def get_object(self):
#     queryset = self.filter_queryset(self.get_queryset())
#     obj = queryset.get(pk=self.request.user.id)
#     self.check_object_permissions(self.request, obj)
#     return obj


# queryset = self.filter_queryset(self.get_queryset())
# obj = queryset.get(user=self.request.user)
# self.check_object_permissions(self.request, obj)
# return obj

# def put(self, request):
#     profile = get_object_or_404(Profile, user=request.user)
#     serializer = ProfileSerializer(profile, data=request.data)
#     serializer.is_valid(raise_exception=True)
#     serializer.save()
#     return Response(serializer.data, status=status.HTTP_201_CREATED)


# serializers.py

# from rest_framework.authtoken.models import Token
# from rest_framework.response import Response
# from drf_writable_nested.serializers import WritableNestedModelSerializer


# Login Serializer
# class LoginSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(required=True)
#     password = serializers.CharField(
#         required=True, style={"input_type": "password"}, write_only=True
#     )

#     token = serializers.CharField(read_only=True)
#     message = serializers.CharField(read_only=True)

#     class Meta:
#         model = User
#         fields = ["email", "password", "token", "message"]

#     def validate(self, obj):
#         try:
#             user = User.objects.get(email=obj["email"])
#         except Exception as e:
#             raise ValidationError({"user": "User not found!", "error": str(e)})

#         if not user.check_password(obj["password"]):
#             raise ValidationError({"password": "Incorrect Login Credentials!"})

#         if not user.is_active:
#             raise ValidationError({"user": "User is not active!"})

#         return obj

#     def create(self, validated_data):
#         user = User.objects.get(email=validated_data["email"])
#         token, _ = Token.objects.get_or_create(user=user)
#         data = {
#             "message": "User Logged In!",
#             "email": validated_data["email"],
#             "token": str(token),
#         }
#         return data


# tasks
# import threading

# class EmailThread(threading.Thread):
#     def __init__(self, email):
#         self.email = email
#         threading.Thread.__init__(self)

#     def run(self):
#         self.email.send()

# EmailThread(email).start()
