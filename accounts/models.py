from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import EmailMessage, BadHeaderError
from django.template.loader import render_to_string
from django.http import HttpResponse

import uuid
import random
import threading

from .managers import UserManager
from base.models import BaseModel

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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']   

    objects = UserManager()

    class Meta:
        ordering = ['-date_joined']
        
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email     
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


def send_email(user):
    print(1)
    current_site = "127.0.0.1:8000"
    email_subject = 'Activate your account!'
    email_body = render_to_string('activate_account.html',{
        'domain': current_site,
        'user': user,
    })
    print(email_body)
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    try:
        email = EmailMessage(subject=email_subject, body=email_body, from_email=from_email, to=recipient_list)
    except BadHeaderError:
        return HttpResponse('Invalid header found.')
    EmailThread(email).start()
    return email.send(fail_silently=False)
    
    
@receiver(post_save, sender=User)
def generate_otp(sender, instance, created, **kwargs):
    try: 
        if created:
            user = instance
            user.otp = random.randint(100000,999999)
            user.save()
            print("http://127.0.0.1:8000/api/activate-user/" + str(user.id) + "/" + str(user.otp) + "/")
            send_email(user)         
    except Exception as e:
        print(e)


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255, null=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True, default="avatar.jpg", upload_to="profile/")
    location = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.name


# Create Profile Signals
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(
            user = instance,
            name = instance.first_name + " " + instance.last_name,
            email = instance.email,
        )
        profile.save()


# Update User Signals
@receiver(post_save, sender=Profile)     
def update_user(sender, instance, created, **kwargs):
    if not created:
        user = instance.user
        user.first_name = instance.name.split(' ')[0]
        user.last_name = instance.name.split(' ')[1]  if len(instance.name.split(' ')) > 1 else ' '
        user.email = instance.email
        user.save()


# Delete User Signals
@receiver(post_delete, sender=Profile)
def delete_user(sender, instance,**kwargs):
    instance.user.delete()