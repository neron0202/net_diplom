import django.dispatch
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django_rest_passwordreset.signals import reset_password_token_created

from .models import ConfirmEmailToken, User


new_user_registered = django.dispatch.Signal(providing_args=['user_id'])
new_order = django.dispatch.Signal(providing_args=['user_id'])

@django.dispatch.receiver(new_user_registered)
def new_user_registered_signal(user_id, **kwargs):
    token, created = ConfirmEmailToken.objects.get_or_create(user_id=user_id)
    msg = EmailMultiAlternatives(
        f"Password Reset Token for{token.user.email}",
        token.key,
        settings.EMAIL_HOST_USER,
        [token.user.email],
    )
    msg.send()


@django.dispatch.receiver(new_order)
def new_order_signal(user_id, **kwargs):
    user = User.objects.get(id=user_id)
    msg = EmailMultiAlternatives(f"Обновление статуса заказа", "Заказ сформирован",
                                 settings.EMAIL_HOST_USER, [user.email])
    msg.send()


@django.dispatch.receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    msg = EmailMultiAlternatives(
        f"password reset token for {reset_password_token.user}",
        reset_password_token.key,
        settings.EMAIL_HOST_USER,
        [reset_password_token.user.email]
    )
    msg.send()
