from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.authtoken.models import Token
from drf_writable_nested.serializers import WritableNestedModelSerializer
from django.shortcuts import get_object_or_404
from django.db.models import *

from cart.models import *


#  Getting cart id from session id
# def _get_cart_id(request):
#     cart_id = request.session.session_key
#     if not cart_id:
#         cart_id = request.session.create()
#     return cart_id


# User Serializer
class UserSerializer(serializers.ModelSerializer):
    email = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = User
        fields = ["email"]


# Product Cart Serializer
class ProductCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price"]


# CartItem Serializer
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductCartItemSerializer()
    size = serializers.StringRelatedField()
    color = serializers.StringRelatedField()
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ["product", "size", "color", "quantity", "total_price"]
        
    def get_total_price(self, cart_item:CartItem):
        return cart_item.product.price * cart_item.quantity
        # return CartItem.objects.annotate(total_price=F('product__price')*F('quantity'))


# Cart Serializer
class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    items = CartItemSerializer(many=True, read_only=True)
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [ "user", "items", "sub_total"]
        
    def get_sub_total(self, cart:Cart):
        return sum([(item.product.price * item.quantity) for item in cart.items.all()])

    
# Add To Cart Serializer
class AddToCartSerializer(serializers.ModelSerializer):
    # product = serializers.UUIDField()

    class Meta:
        model = CartItem
        fields = ['product', 'size', 'color']
    
    def save(self, **kwargs):
        user = self.context['user']
        product = self.validated_data['product']
        cart, _ = Cart.objects.get_or_create(user=user)
            
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(cart=cart, product=product, quantity=1)
            
        return cart_item


# Delete From Cart Serializer
class DeleteFromCartSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField(required=False)    
    quantity = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = CartItem
        fields = ["product", "quantity"]
    
    def save(self, **kwargs):
        product = self.context['product']
        user = self.context['user'] 
        cart = get_object_or_404(Cart, user=user)
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        
        return cart_item


# Remove From Cart Serializer
class RemoveFromCartSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CartItem
        # fields = ["product"]
    
    def save(self, **kwargs):
        product = self.context['product']
        user = self.context['user']
        cart = get_object_or_404(Cart, user=user)   
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        cart_item.delete()
        return cart_item
