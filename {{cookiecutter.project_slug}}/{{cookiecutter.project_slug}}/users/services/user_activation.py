from django.db import transaction

from .user_token import UserTokenService
from {{cookiecutter.project_slug}}.users.models import User, UserToken, TokenTypes


class UserActivationService(UserTokenService):
    def __init__(self, *args, **kwargs):
        super(UserActivationService).__init__(*args, **kwargs)

    @transaction.atomic
    def request(self, user: User):
        token = UserToken.objects.create(
            user=user,
            token_type=TokenTypes.ACTIVATION.value,
        )
        # Send email
        # ... (you can inject or call email handlers here)

    @transaction.atomic
    def perform(self, password):
        self._check_validity()
        user = self.user_token.user
        user.set_password(password)
        user.is_active = True
        user.save()
        self.user_token.used = True
        self.user_token.save()
        # Send email and register user
        # ... (you can inject or call email handlers here)
        return user
