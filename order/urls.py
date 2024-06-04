from django.urls import path

from .views import *

urlpatterns = [
    path("checkout/", CheckoutList.as_view()),
    path("checkout/<str:pk>/", CheckoutDetail.as_view()),
    path("payment/", PaymentList.as_view()),
    path("payment/callback/", RazorpayCallbackView.as_view(), name="razorpay-callback"),
    path("", OrderList.as_view()),
    path("<str:pk>/", OrderDetail.as_view()),
]
