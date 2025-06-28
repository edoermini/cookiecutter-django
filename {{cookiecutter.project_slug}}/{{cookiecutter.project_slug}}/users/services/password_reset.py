from django.db import transaction

from {{ cookiecutter.project_slug }}.users.models import TokenTypes
from {{ cookiecutter.project_slug }}.users.models import User
from {{ cookiecutter.project_slug }}.users.models import UserToken

from .user_token import UserTokenService


class PasswordResetService(UserTokenService):
    def __init__(self, *args, **kwargs):
        super(PasswordResetService).__init__(*args, **kwargs)

    @transaction.atomic
    def request(self, user: User):
        UserToken.objects.create(
            user=user,
            token_type=TokenTypes.PASSWORD_RESET.value,
        )
        # Send email
        # ... (you can inject or call email handlers here)

    @transaction.atomic
    def perform(self, password):
        self._check_validity()
        user = self.user_token.user
        user.set_password(password)
        user.save()
        self.user_token.used = True
        self.user_token.save()
        # Send email and register user
        # ... (you can inject or call email handlers here)
        return user
