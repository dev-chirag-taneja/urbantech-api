from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)
from rest_framework import status
from django.utils import timezone
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db import transaction
import razorpay

from .serializers import *
from .models import Order, OrderItem

# Create your views here.


# Checkout Api
class CheckoutList(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        cart = get_object_or_404(Cart, user=user)

        if not cart.items.exists():
            return Response(
                {"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        address_serializer = AddressSerializer(
            data=request.data, context={"user": user}
        )
        address_serializer.is_valid(raise_exception=True)
        address_serializer.save(user=user)
        return Response(address_serializer.data, status=status.HTTP_201_CREATED)


# Payment Api
class PaymentList(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        total_amount = cart.get_sub_total
        if total_amount is None:
            return Response(
                {"error": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment_option = request.data.get("payment_option")

        if payment_option == "cod":
            with transaction.atomic():
                payment = Payment.objects.create(
                    user=request.user,
                    payment_option="cod",
                    amount=total_amount,
                    successful=False,
                )

                # creating order and order items
                order = Order.objects.create(
                    user=payment.user, payment_option="cod", total_amount=payment.amount
                )

                order_items = [
                    OrderItem(
                        order=order,
                        product=item.product,
                        size=item.size,
                        color=item.color,
                        quantity=item.quantity,
                        unit_price=item.product.price,
                    )
                    for item in cart.items.all()
                ]
                OrderItem.objects.bulk_create(order_items)

                payment.order = order
                payment.save()

                address = Address.objects.filter(user=request.user).latest("created_at")
                address.order = order
                address.save()

                # deleting the user's cart
                # cart.delete()

                return Response(
                    {"message": "Order created."},
                    status=status.HTTP_200_OK,
                )

        elif payment_option == "razorpay":
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )

            data = {
                "amount": int(total_amount) * 100,
                "currency": "INR",
                "receipt": "order_receipt",
            }
            try:
                razorpay_order = client.order.create(data=data)
            except razorpay.errors.BadRequestError:
                return Response(
                    {"error": "Error creating Razorpay order"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            payment = Payment.objects.create(
                user=request.user,
                payment_option="razorpay",
                razorpay_order_id=razorpay_order.get("id"),
                amount=total_amount,
                successful=False,
            )
            serializer = self.get_serializer(payment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response(
                {"error": "Invalid payment option"}, status=status.HTTP_400_BAD_REQUEST
            )


# Razorpay Callback Api
class RazorpayCallbackView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        payment.successful = True
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.save()

        # creating order and order items
        cart = Cart.objects.get(user=payment.user)
        order = Order.objects.create(
            user=payment.user,
            payment_option="razorpay",
            payment_status="complete",
            total_amount=payment.amount,
            is_paid=True,
            paid_at=timezone.now(),
        )

        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                size=item.size,
                color=item.color,
                quantity=item.quantity,
                unit_price=item.product.price,
            )
            for item in cart.items.all()
        ]
        OrderItem.objects.bulk_create(order_items)

        payment.order = order
        payment.save()

        address = Address.objects.filter(user=request.user).latest("created_at")
        address.order = order
        address.save()

        # deleting the user's cart
        cart.delete()

        return Response(
            {"message": "Payment successful. Order created."}, status=status.HTTP_200_OK
        )


# Order Api
class OrderList(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_admin:
            return Order.objects.prefetch_related("items__product", "user").all()
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "items__product"
        )


# Order Api (for admin)
class OrderDetail(generics.DestroyAPIView):
    permission_classes = [IsAdminUser | IsAuthenticatedOrReadOnly]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
