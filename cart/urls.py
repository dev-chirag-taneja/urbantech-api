from django.urls import path

from .views import *

urlpatterns = [
    path("", CartList.as_view()),
    path("add-to-cart/", AddToCartList.as_view()),
    path("delete-from-cart/<str:product_id>/", DeleteFromCartDetail.as_view()),
    path("remove-from-cart/<str:product_id>/", RemoveFromCartDetail.as_view()),
]
