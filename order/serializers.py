from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.forms import ValidationError

from order.models import Address, Payment, Order, OrderItem
from cart.models import Cart, CartItem
from cart.serializers import ProductCartItemSerializer, UserSerializer


# Address Serializer
class AddressSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Address
        fields = ["id", "user", "address", "zip_code", "city", "state", "country"]

    def create(self, validated_data):
        user = self.context.get("request").user
        cart = get_object_or_404(Cart, user=user)

        if not cart.items.exists():
            raise serializers.ValidationError({"error": "Cart is empty"})

        address = Address.objects.create(user=user, **validated_data)
        return address

    def update(self, instance, validated_data):
        if (
            self.context["request"].user.is_staff
            or instance.user == self.context["request"].user
        ):
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance
        else:
            raise serializers.ValidationError(
                {"message": "You don't have permission to perform this action."}
            )


# Payment Serializer
class PaymentSerializer(serializers.ModelSerializer):
    address = serializers.UUIDField(required=True)

    class Meta:
        model = Payment
        fields = ("payment_option", "address", "amount", "successful", "timestamp")
        read_only_fields = ("amount", "successful", "timestamp")


# OrderItem Serializer
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
