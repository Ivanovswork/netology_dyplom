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


@shared_task()
def send_email_about_comfirming_order(key, order_id, email):
    sleep(10)

    send_mail(
        "destira@mail.ru",
        f"http://127.0.0.1:8000/confirm_order/{key}/{order_id}/",
        EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )


@shared_task()
def send_email_about_comfirmed_order(order_id, email):
    sleep(10)

    send_mail(
        "destira@mail.ru",
        f"Ваш заказ подтвержен. Его номер {order_id}. Спасибо за выбор нашего сервиса",
        EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )


@shared_task()
def send_email_about_order_for_shop(name, quantity, staff):
    send_mail(
        f"В вашем магазине был совершен заказ на товар: {name} в количестве "
        f"{quantity}",
        EMAIL_HOST_USER,
        staff,
        fail_silently=False,
    )