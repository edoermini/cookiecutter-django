from datetime import timedelta

from django.conf import settings
from django.utils.timezone import now

from rest_framework import serializers

from {{ cookiecutter.project_slug }}.users.models import User, UserToken, TokenTypes


class UserActivationRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        if user.is_active:
            raise serializers.ValidationError("User is already active.")
        return value


class UserActivationConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
    )

    def validate(self, attrs):
        try:
            user_token = UserToken.objects.get(
                token=attrs['token'],
                token_type=TokenTypes.ACTIVATION.value,
                used=False,
                created_at__gte=now() - timedelta(hours=settings.TOKEN_EXPIRY_HOURS)
            )
        except UserToken.DoesNotExist:
            raise serializers.ValidationError("Token invalid.")

        attrs['user_token'] = user_token
        return attrs
