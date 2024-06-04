from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from cart.models import *


def create_payment_and_order(
    self, request, total_amount, payment_option, razorpay_order_id=None
):
    payment = Payment.objects.create(
        user=request.user,
        payment_option=payment_option,
        amount=total_amount,
        successful=False,
        razorpay_order_id=razorpay_order_id,
    )

    order = Order.objects.create(
        user=payment.user,
        payment_option=payment_option,
        total_amount=payment.amount,
    )

    payment.order = order
    payment.save()

    return payment, order


def create_order_items(self, cart, order):
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


def link_address_to_order(self, address, order):
    address.order = order
    address.save()


def get_latest_address(user):
    try:
        return Address.objects.filter(user=user).latest("created_at")
    except ObjectDoesNotExist:
        return None
