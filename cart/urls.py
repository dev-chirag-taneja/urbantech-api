from django.urls import path

from .views import *

urlpatterns = [
    path('cart/', CartList.as_view()),
    path('cart/add-to-cart/', AddToCartList.as_view()),
    path('cart/delete-from-cart/<str:product_id>/', DeleteFromCartDetail.as_view()),
    path('cart/remove-from-cart/<str:product_id>/', RemoveFromCartDetail.as_view()),
]