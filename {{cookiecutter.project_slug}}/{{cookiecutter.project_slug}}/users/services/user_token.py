from datetime import timedelta

from django.conf import settings
from django.utils.timezone import now

from {{cookiecutter.project_slug}}.users.models import UserToken, TokenTypes

class TokenExpiredException(Exception):
    pass

class TokenUsedException(Exception):
    pass

class InvalidTokenTypeException(Exception):
    pass

class TokenNotLinkedToUserException(Exception):
    pass

class UserTokenService:
    def __init__(self, user_token: UserToken = None):
        self.user_token = user_token

    def _check_validity(self):
        validity_time = now() - timedelta(hours=settings.TOKEN_EXPIRY_HOURS)

        if self.user_token.used:
            raise TokenUsedException("Token already used")
        if self.user_token.token_type != TokenTypes.ACTIVATION.value:
            raise InvalidTokenTypeException("Wrong token type")
        if self.user_token.created_at < validity_time:
            raise TokenExpiredException("Token expired")
