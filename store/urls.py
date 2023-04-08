from django.urls import path

from .views import *

urlpatterns = [
    path('category/', CategoryListView.as_view()),
    path('products/', ProductListView.as_view()),
    path('products/<str:slug>/', ProductDetailView.as_view()),
    path('products/<str:slug>/images/', ProductImageListView.as_view()),
    path('products/<str:slug>/images/<str:pk>/', ProductImageDetailView.as_view()),
    path('products/<str:slug>/reviews/', ReviewListView.as_view()),
    path('products/<str:slug>/reviews/<str:pk>/', ReviewDetailView.as_view()),
    
    # uuid instead of slug
    # path('products/<str:uuid>/images/<str:pk>/', ProductImageDetailView.as_view()),
    # path('products/<str:uuid>/reviews/<str:pk>/', ReviewDetailView.as_view()),
]