from datetime import timedelta

import pytest
from django.conf import settings

from {{ cookiecutter.project_slug }}.users.models import TokenTypes
from {{ cookiecutter.project_slug }}.users.models import User
from {{ cookiecutter.project_slug }}.users.models import UserToken


@pytest.mark.django_db
class TestUserManager:
    def test_create_user(self):
        user = User.objects.create_user(
            email="john@example.com",
            password="something-r@nd0m!",  # noqa: S106
        )
        assert user.email == "john@example.com"
        assert not user.is_staff
        assert not user.is_superuser
        assert user.check_password("something-r@nd0m!")
        assert user.username is None

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="something-r@nd0m!",  # noqa: S106
        )
        assert user.email == "admin@example.com"
        assert user.is_staff
        assert user.is_superuser
        assert user.username is None

    def test_create_superuser_username_ignored(self):
        user = User.objects.create_superuser(
            email="test@example.com",
            password="something-r@nd0m!",  # noqa: S106
        )
        assert user.username is None

@pytest.mark.django_db
class TestUserTokenManager:

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            email="john@example.com",
            password="something-r@nd0m!",  # noqa: S106
        )

    @pytest.fixture
    def valid_token(self, user):
        return UserToken.objects.create(user=user, token_type=TokenTypes.ACTIVATION)

    @pytest.fixture
    def expired_token(self, user):
        token = UserToken.objects.create(user=user,token_type=TokenTypes.ACTIVATION)
        token.created_at = token.created_at - \
            timedelta(hours=settings.TOKEN_EXPIRY_HOURS+1)

        token.save()

        return token

    def test_valid_tokens(self, valid_token, expired_token):
        tokens = UserToken.objects.valid_tokens()

        assert len(tokens) == 1
        assert tokens.filter(token=valid_token.token).exists()
        assert not tokens.filter(token=expired_token.token).exists()
