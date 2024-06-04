from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

from .views import *

urlpatterns = [
    # user
    path("register/", RegisterView.as_view()),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("change-password/", ChangePasswordView.as_view()),
    path(
        "activate-user/<str:pk>/<str:otp>/",
        ActivateUserView.as_view(),
        name="activate_user",
    ),
    path(
        "resend-activation/",
        ResendActivationEmailView.as_view(),
        name="resend_activation",
    ),
    # reset password
    path(
        "reset-password/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "reset-password-confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # profile
    path("profiles/", ListUserView.as_view()),
    path("profile/", ProfileDetailView.as_view()),
    path("profiles/<str:pk>/", DeleteUserView.as_view()),
]
