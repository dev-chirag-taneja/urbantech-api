from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import *

urlpatterns = [
    
    # User
    path('register/', RegisterView.as_view()),
    # path('login/', LoginView.as_view()),
    # path('logout/', LogoutView.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordView.as_view()),
    path('activate-user/<str:pk>/<str:otp>/', ActivateUserView.as_view(), name='activate_user'),

    # Profile
    path('profile/', ProfileDetailView.as_view()),
    path('profiles/', ListUserView.as_view()), 
    path('profiles/<str:pk>/', DeleteUserView.as_view()),
]