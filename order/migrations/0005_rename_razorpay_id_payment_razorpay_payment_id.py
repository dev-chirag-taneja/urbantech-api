# Generated by Django 4.1.7 on 2023-07-26 05:36

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0004_alter_payment_amount"),
    ]

    operations = [
        migrations.RenameField(
            model_name="payment",
            old_name="razorpay_id",
            new_name="razorpay_payment_id",
        ),
    ]
