from django.core.mail import EmailMessage, BadHeaderError
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail


# Task 1
@shared_task
def send_email(user):
    User = get_user_model()
    try:
        user = User.objects.get(id=user)
        current_site = "127.0.0.1:8000"
        email_subject = "Activate your account!"
        email_body = render_to_string(
            "activate_account.html",
            {
                "domain": current_site,
                "user": user,
            },
        )
        # print(email_body)
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        email = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email=from_email,
            to=recipient_list,
        )
        email.send(fail_silently=False)
    except User.DoesNotExist:
        return HttpResponse("User does not exist.")
    except BadHeaderError:
        return HttpResponse("Invalid header found.")


# Task 2
@shared_task
def send_mail_link(subject, message, from_email, to_email):
    try:
        send_mail(subject, message, from_email, to_email, fail_silently=False)
    except Exception as e:
        print(f"Failed to send email: {e}")
