# Generated by Django 4.1.7 on 2023-07-26 04:47

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0002_alter_orderitem_unit_price"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="payment",
            options={"verbose_name": "Payment", "verbose_name_plural": "Payments"},
        ),
        migrations.RemoveField(
            model_name="address",
            name="order",
        ),
    ]