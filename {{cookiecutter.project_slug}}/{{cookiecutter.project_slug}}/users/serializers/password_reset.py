from datetime import timedelta

from django.conf import settings
from django.utils.timezone import now
from rest_framework import serializers

from {{ cookiecutter.project_slug }}.users.models import TokenTypes
from {{ cookiecutter.project_slug }}.users.models import User
from {{ cookiecutter.project_slug }}.users.models import UserToken

from .exceptions import InvalidTokenError
from .exceptions import UserDoesNotExistError
from .exceptions import UserNotActiveError


class UserPasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise UserDoesNotExistError from None
        if not user.is_active:
            raise UserNotActiveError
        return value

class UserPasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
    )

    def validate(self, attrs):
        try:
            user_token = UserToken.objects.get(
                token=attrs["token"],
                token_type=TokenTypes.PASSWORD_RESET.value,
                used=False,
                created_at__gte=now() - timedelta(hours=settings.TOKEN_EXPIRY_HOURS),
            )
        except UserToken.DoesNotExist:
            raise InvalidTokenError from None

        attrs["user_token"] = user_token
        return attrs
