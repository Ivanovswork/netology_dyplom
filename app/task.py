from time import sleep

from django.conf.global_settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from celery import shared_task

@shared_task()
def send_email(key, email):
    sleep(10)

    send_mail(
        "destira@mail.ru",
        f"http://127.0.0.1:8000/confirm/{key}/",
        EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

