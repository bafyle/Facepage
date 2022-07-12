from typing import Tuple

from django.http.request import HttpRequest
from .id_generator import id_generator
from django.contrib.auth import get_user_model as User
from django.http import HttpRequest
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from .tokens import account_activation_token
from .constants import ID_LENGTH

def create_user_link(user: User()) -> str:
    while True:
        id_generated = id_generator(user, ID_LENGTH)
        if not User().objects.filter(profile__link=id_generated).exists():
            return id_generated


def send_activate_email(request: HttpRequest, user: User(), failSilently: bool = False) -> Tuple[int, str, str]:
    """
    This is not a view function, it sends an email with
    an activation link and returns tuple with
    int: 1 if email send successfully
    str: the uid of the user
    str: the token of the user
    """
    current_site = get_current_site(request)
    mail_subject = 'Activate your Facepage account.'
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    message = render_to_string('pages/AccountActivation.html', {
        'user': user,
        'domain': current_site.domain,
        'uid':uid,
        'token':token,
        'protocol': 'https' if settings.SECURE_SSL_REDIRECT else 'http' 
    })
    email = EmailMessage(
            mail_subject,
            message,
            to=[user.email],
    )
    return email.send(fail_silently=failSilently), uid, token


def send_new_password(password, email, fail_silently: bool = False):
    """
    Not view function, It sends a new password to user email
    if this user forgot his password
    """
    mail_subject = 'Facepage: password reset'
    message = f"""
Your new password is: {password}\nPlease do NOT share it with anyone and
don't forget to change your password once you log in to Facepage again\n
AND DO NOT FORGET IT AGAIN!!! """
    email = EmailMessage(
            mail_subject,
            message,
            to=[email],
    )
    return email.send(fail_silently=fail_silently)
