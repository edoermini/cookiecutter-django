from django.conf import settings
from django.db import transaction

from _common.utils.email import send_email
from {{ cookiecutter.project_slug }}.users.models import User
from {{ cookiecutter.project_slug }}.users.models import UserToken
from {{ cookiecutter.project_slug }}.users.models.enums import TokenTypes

from .user_token import UserTokenService


class PasswordResetService(UserTokenService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @transaction.atomic
    def request(self, user: User):
        token = UserToken.objects.create(
            user=user,
            token_type=TokenTypes.PASSWORD_RESET,
        )

        send_email(
            subject="Account activation",
            body=f"""
            Click the link below to reset your password: \n
            {settings.BASE_URL_FRONTEND}/password-reset?token={token.token}
            """,
            to=[user.email],
        )

    @transaction.atomic
    def confirm(self, password):
        self._check_validity()
        user = self.user_token.user
        user.set_password(password)
        user.save()
        self.user_token.used = True
        self.user_token.save()

        send_email(
            subject="Password changed successfully.",
            body="Your password has been changed",
            to=[user.email],
        )

        return user
