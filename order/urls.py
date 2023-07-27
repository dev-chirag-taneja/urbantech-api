from django.urls import path

from .views import *

urlpatterns = [
    path("checkout/", CheckoutList.as_view()),
    path("payment/", PaymentList.as_view()),
    path(
        "razorpay/callback/", RazorpayCallbackView.as_view(), name="razorpay-callback"
    ),
    path("order/", OrderList.as_view()),
    path("order/<str:pk>/", OrderDetail.as_view()),
]
