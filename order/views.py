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
from .utils import *
from .models import Order


# Checkout View
class CheckoutList(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


# Checkout Detail View
class CheckoutDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated | IsAdminUser]

    def get_queryset(self):
        return Address.objects.filter(id=self.kwargs["pk"], user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        try:
            address = Address.objects.get(id=self.kwargs["pk"])
            if request.user.is_staff or address.user == request.user:
                address.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    data={
                        "message": "You dont have permission to perform this action!"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ObjectDoesNotExist:
            return Response(
                data={"message": "Address not found!"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# Payment View
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
        address_uuid = request.data.get("address")

        if not payment_option:
            return Response(
                {"error": "Invalid payment option"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not address_uuid:
            return Response(
                {"error": "Address is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            address = Address.objects.get(pk=address_uuid, user=request.user)
        except Address.DoesNotExist:
            return Response(
                {"error": "Address not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if payment_option == "cod":
            with transaction.atomic():
                payment, order = create_payment_and_order(
                    self, request, total_amount, payment_option="cod"
                )

                create_order_items(self, cart, order)
                link_address_to_order(self, address, order)
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

            payment, order = create_payment_and_order(
                self,
                request,
                total_amount,
                payment_option="razorpay",
                razorpay_order_id=razorpay_order.get("id"),
            )
            # order items is not created, only after successful payment
            link_address_to_order(self, address, order)

            return Response(
                {"message": "Order created."},
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                {"error": "Invalid payment option"}, status=status.HTTP_400_BAD_REQUEST
            )


# Razorpay Callback View
class RazorpayCallbackView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        # Validate Razorpay signature
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }

        try:
            client.utility.verify_payment_signature(params_dict)
        except razorpay.errors.SignatureVerificationError:
            return Response(
                {"error": "Invalid Razorpay signature"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        with transaction.atomic():
            payment.successful = True
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.save()

            cart = Cart.objects.get(user=payment.user)
            order = payment.order
            create_order_items(
                cart, order
            )  # creating order items after successful payment
            cart.delete()

        return Response(
            {"message": "Payment successful. Order created."}, status=status.HTTP_200_OK
        )


# Order View
class OrderList(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_admin:
            return Order.objects.prefetch_related("items__product").all()
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "items__product"
        )


# Order View (for admin)
class OrderDetail(generics.DestroyAPIView):
    permission_classes = [IsAdminUser | IsAuthenticatedOrReadOnly]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
