from datetime import timedelta

from django.conf import settings
from django.utils.timezone import now

from {{ cookiecutter.project_slug }}.users.models import TokenTypes
from {{ cookiecutter.project_slug }}.users.models import UserToken

from .exceptions import InvalidTokenTypeError
from .exceptions import TokenAlreadyUsedError
from .exceptions import TokenExpiredError


class UserTokenService:
    def __init__(self, user_token: UserToken = None):
        self.user_token = user_token

    def _check_validity(self):
        validity_time = now() - timedelta(hours=settings.TOKEN_EXPIRY_HOURS)

        if self.user_token.used:
            raise TokenAlreadyUsedError
        if self.user_token.token_type != TokenTypes.ACTIVATION.value:
            raise InvalidTokenTypeError
        if self.user_token.created_at < validity_time:
            raise TokenExpiredError
