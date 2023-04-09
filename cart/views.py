from rest_framework.response import Response
from rest_framework import generics 
from rest_framework.permissions import IsAuthenticated

from .serializers import *

# Cart Api
class CartList(generics.ListAPIView):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_context(self):
        return {'user':self.request.user}


# Add To Cart
class AddToCartList(generics.CreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = AddToCartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_context(self):
        return {'user':self.request.user}


# Delete From Cart
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
        return {'user':self.request.user, 'product':self.kwargs['product_id']}


# Remove From Cart
class RemoveFromCartDetail(generics.DestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = RemoveFromCartSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "product_id"

    def get_serializer_context(self):
        return {'user':self.request.user, 'product':self.kwargs['product_id']}



# Cart Api (Only For Admin)
# class CartDetail(generics.RetrieveDestroyAPIView):
#     queryset = Cart.objects.prefetch_related('items__product').all()
#     serializer_class = CartSerializer