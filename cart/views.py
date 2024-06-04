from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .serializers import *


# Cart View
class CartList(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Cart.objects.filter(user=self.request.user)
            .prefetch_related("items__product", "user")
            .all()
        )
    
    def list(self, request, *args, **kwargs):
        # Generate a unique cache key using the user's ID
        cache_key = f'cart_list_{request.user.id}'
        cached_cart_data = cache.get(cache_key)
        if cached_cart_data is not None:
            return Response(cached_cart_data)

        # If cache is empty, fetch data from the database
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Cache the fetched data with a timeout of 30 seconds
        cached_cart_data = serializer.data
        cache.set(cache_key, cached_cart_data, timeout=30)

        return Response(cached_cart_data)


# Add To Cart View
class AddToCartList(generics.CreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = AddToCartSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {"user": self.request.user}


# Delete From Cart View
class DeleteFromCartDetail(generics.UpdateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = DeleteFromCartSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "product_id"

    # def get_object(self):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     obj = queryset.get(product_id=self.kwargs['uuid'])
    #     self.check_object_permissions(self.request, obj)
    #     return obj

    def get_serializer_context(self):
        return {"user": self.request.user, "product": self.kwargs["product_id"]}


# Remove From Cart View
class RemoveFromCartDetail(generics.DestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = RemoveFromCartSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "product_id"

    def get_serializer_context(self):
        return {"user": self.request.user, "product": self.kwargs["product_id"]}


# Cart Api (Only For Admin)
# class CartDetail(generics.RetrieveDestroyAPIView):
#     queryset = Cart.objects.prefetch_related('items__product').all()
#     serializer_class = CartSerializer
