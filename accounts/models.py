from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

import uuid
import random

from .managers import UserManager
from base.models import BaseModel
from .tasks import send_email


# Create your models here.
class User(AbstractBaseUser):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    first_name = models.CharField(max_length=20, null=True)
    last_name = models.CharField(max_length=20, null=True)
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=10, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        ordering = ["-date_joined"]

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


@receiver(post_save, sender=User)
def generate_otp(sender, instance, created, **kwargs):
    try:
        if created:
            user = instance
            user.otp = random.randint(100000, 999999)
            user.save()
            print(
                f"http://127.0.0.1:8000/api/auth/activate-user/{str(user.id)}/{str(user.otp)}/"
            )
            send_email.delay(user.id)
    except Exception as e:
        print(e)


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255, null=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    avatar = models.ImageField(
        null=True, blank=True, default="avatar.jpg", upload_to="profile/"
    )
    location = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


# Create Profile Signals
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(
            user=instance,
            name=instance.first_name + " " + instance.last_name,
            email=instance.email,
        )
        profile.save()


# Update User Signals
@receiver(post_save, sender=Profile)
def update_user(sender, instance, created, **kwargs):
    if not created:
        user = instance.user
        user.first_name = instance.name.split(" ")[0]
        user.last_name = (
            instance.name.split(" ")[1] if len(instance.name.split(" ")) > 1 else " "
        )
        user.email = instance.email
        user.save()


# Delete User Signals
@receiver(post_delete, sender=Profile)
def delete_user(sender, instance, **kwargs):
    instance.user.delete()
