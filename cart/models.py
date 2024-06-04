from django.db import models
from django.db.models import *
from decimal import Decimal

from store.models import Product, ProductSizeVariant, ProductColorVariant
from accounts.models import User

# Create your models here.


# Cart
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_sub_total(self):
        subtotal = self.items.aggregate(
            sub_total=Sum(
                F("product__price") * F("quantity"), output_field=DecimalField()
            )
        )["sub_total"] or Decimal(0)

        return subtotal
        # return sum([(item.product.price * item.quantity) for item in self.items.all()])

    def __str__(self):
        return str(self.user.email)


# Cart Item
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, null=True, blank=True, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(
        ProductSizeVariant, on_delete=models.SET_NULL, null=True, blank=True
    )
    color = models.ForeignKey(
        ProductColorVariant, on_delete=models.SET_NULL, null=True, blank=True
    )
    quantity = models.PositiveIntegerField()

    @property
    def get_total(self) -> float:
        return self.product.price * self.quantity

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name}"
