from django.db import models
import uuid
from store.models import Product, ProductSizeVariant, ProductColorVariant
from accounts.models import User
from base.models import BaseModel

# Create your models here.
PAYMENT_OPTION = (
    ("cod", "cod"),
    ("razorpay", "razorpay"),
)


class Order(models.Model):
    ORDER_STATUS = (
        ("Not Yet Shipped", "Not Yet Shipped"),
        ("Shipped", "Shipped"),
        ("Cancelled", "Cancelled"),
    )
    PAYMENT_STATUS = (
        ("Pending", "Pending"),
        ("Complete", "Complete"),
        ("Failed", "Failed"),
    )

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    order_no = models.CharField(max_length=20)
    order_status = models.CharField(
        max_length=20, choices=ORDER_STATUS, default="Not Yet Shipped"
    )
    payment_option = models.CharField(max_length=20, choices=PAYMENT_OPTION)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS, default="Pending"
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    is_delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.reference_number

    @property
    def reference_number(self) -> str:
        return f"Order-{self.pk}"

    def save(self, *args, **kwargs):
        if not self.order_no:
            uuid_str = str(uuid.uuid4().int)[
                :20]
            self.order_no = "-".join([uuid_str[i:i+5] for i in range(0, len(uuid_str), 5)])
        super(Order, self).save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    size = models.ForeignKey(
        ProductSizeVariant, on_delete=models.SET_NULL, null=True, blank=True
    )
    color = models.ForeignKey(
        ProductColorVariant, on_delete=models.SET_NULL, null=True, blank=True
    )
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name}"


class Address(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    order = models.OneToOneField(
        Order, on_delete=models.SET_NULL, related_name="shipping_address", null=True
    )
    address = models.TextField()
    zip_code = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

    def full_address(self) -> str:
        return ", ".join(
            [self.address, self.zip_code, self.city, self.state, self.country]
        )

    def __str__(self) -> str:
        return f"{self.user} - {self.city}"


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    payment_option = models.CharField(max_length=20, choices=PAYMENT_OPTION)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    successful = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self) -> str:
        return self.reference_number

    @property
    def reference_number(self) -> str:
        return f"{self.user.email}-{self.amount}"
