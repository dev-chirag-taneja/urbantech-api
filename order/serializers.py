from rest_framework import serializers

from order.models import Address, Payment, Order, OrderItem
from cart.models import Cart, CartItem
from cart.serializers import ProductCartItemSerializer, UserSerializer


# class CheckoutItemSerializer(serializers.ModelSerializer):
#     product_name = serializers.ReadOnlyField(source="product.name")
#     product_price = serializers.ReadOnlyField(source="product.price")
#     total_price = serializers.SerializerMethodField()

#     class Meta:
#         model = CartItem
#         fields = ["product_name", "product_price", "quantity", "total_price"]

#     def get_total_price(self, instance):
#         return instance.get_total()


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["address", "zip_code", "city", "state", "country"]


# Checkout Serializer
# class CheckoutSerializer(serializers.ModelSerializer):
#     user_email = serializers.ReadOnlyField(source="user.email")
#     sub_total = serializers.SerializerMethodField()
#     items = CheckoutItemSerializer(many=True, read_only=True)
#     shipping_address = AddressSerializer(source="user.address", read_only=True)

#     class Meta:
#         model = Cart
#         fields = ["user_email", "sub_total", "items", "shipping_address"]

#     def get_sub_total(self, instance):
#         return instance.get_sub_total()


# Payment Serializer
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("payment_option", "amount", "successful", "timestamp")
        read_only_fields = ("amount", "successful", "timestamp")


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductCartItemSerializer()
    size = serializers.StringRelatedField()
    color = serializers.StringRelatedField()

    class Meta:
        model = OrderItem
        fields = ["product", "size", "color", "quantity", "unit_price"]


# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "order_no",
            "order_status",
            "payment_option",
            "payment_status",
            "total_amount",
            "is_paid",
            "paid_at",
            "is_delivered",
            "delivered_at",
            "created_at",
            "items",
        )