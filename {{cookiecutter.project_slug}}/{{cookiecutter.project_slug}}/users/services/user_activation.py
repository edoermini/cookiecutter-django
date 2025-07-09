from django.conf import settings
from django.db import transaction

from _common.utils.email import send_email
from {{ cookiecutter.project_slug }}.users.models import TokenTypes
from {{ cookiecutter.project_slug }}.users.models import User
from {{ cookiecutter.project_slug }}.users.models import UserToken

from .user_token import UserTokenService


class UserActivationService(UserTokenService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @transaction.atomic
    def request(self, user: User):
        token = UserToken.objects.create(
            user=user,
            token_type=TokenTypes.ACTIVATION.value,
        )

        send_email(
            subject="Account activation",
            body=f"""
            Click the link below to activate your account: \n
            {settings.BASE_URL_FRONTEND}/activation?token={token.token}
            """,
            to=[user.email],
        )

    @transaction.atomic
    def perform(self, password):
        self._check_validity()
        user = self.user_token.user
        user.set_password(password)
        user.is_active = True
        user.save()
        self.user_token.used = True
        self.user_token.save()

        send_email(
            subject="Account successfully activated",
            body="You account has been successfully activated",
            to=[user.email],
        )

        return user
