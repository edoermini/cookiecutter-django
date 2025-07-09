import uuid

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from {{ cookiecutter.project_slug }}.users.models import User
from {{ cookiecutter.project_slug }}.users.models import UserToken
from {{ cookiecutter.project_slug }}.users.serializers.exceptions import UserAlreadyExistsError
from {{ cookiecutter.project_slug }}.users.serializers.user import UserSerializer

# ruff: noqa: PLR2004

TEST_P = "test_password_123"

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@test.com",
        first_name="Test",
        last_name="Test",
        password=TEST_P,
        is_active=True,
    )

@pytest.fixture
def user2(db):
    return User.objects.create_user(
        email="new-email@test.com",
        first_name="Test",
        last_name="Test",
        password=TEST_P,
        is_active=True,
    )

@pytest.fixture
def inactive_user(db):
    return User.objects.create_user(
        email="test@test.com",
        first_name="Test",
        last_name="Test",
        password=TEST_P,
        is_active=False,
    )


class TestUserViewSet:

    def test_me_unauthorized(self, user: User, api_client: APIClient):
        endpoint = reverse("api:users-me")

        response = api_client.get(endpoint)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_me(self, user: User, api_client: APIClient):
        endpoint = reverse("api:users-me")

        api_client.force_authenticate(user=user)
        response = api_client.get(endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == UserSerializer(user).data

    def test_update_unauthorized(self, user: User, api_client: APIClient):
        endpoint = reverse("api:users-update-profile")

        response = api_client.put(endpoint)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_email_already_in_use(
            self, user: User, user2: User, api_client: APIClient):
        endpoint = reverse("api:users-update-profile")

        data = {"email": "new-email@test.com"}

        api_client.force_authenticate(user=user)
        response = api_client.put(endpoint, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
        assert response.data.get("email")[0] == UserAlreadyExistsError().detail[0]

    @pytest.mark.django_db
    def test_update(self, user: User, api_client: APIClient):
        endpoint = reverse("api:users-update-profile")

        data = {"email": "new-email@test.com"}

        api_client.force_authenticate(user=user)
        response = api_client.put(endpoint, data=data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("email") == data.get("email")

@pytest.mark.django_db
class TestToken:

    def test_obtain_token_pair_inactive_user(
            self, inactive_user: User, api_client: APIClient):
        endpoint = reverse("api:token_obtain_pair")

        data = {
            "email": inactive_user.email,
            "password": TEST_P,
        }

        response = api_client.post(endpoint, data=data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_obtain_pair(self, user: User, api_client: APIClient):
        endpoint = reverse("api:token_obtain_pair")

        data = {
            "email": user.email,
            "password": TEST_P,
        }

        response = api_client.post(endpoint, data=data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

        # testing accessing to restricted view

        access_token = response.data["access"]

        response = api_client.get(reverse("api:users-me"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = api_client.get(reverse("api:users-me"))

        assert response.status_code == status.HTTP_200_OK

    def test_token_refresh(self, user: User, api_client: APIClient):
        endpoint = reverse("api:token_refresh")

        refresh_token = RefreshToken.for_user(user)

        response = api_client.post(endpoint, data={"refresh": refresh_token})

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

        # testing accessing to restricted view

        access_token = response.data["access"]

        response = api_client.get(reverse("api:users-me"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = api_client.get(reverse("api:users-me"))


@pytest.mark.django_db
class TestUserActivation:

    def test_user_activation_request(
        self, inactive_user: User, api_client: APIClient, mocker):

        mock_send_email = mocker.patch(
            "{{cookiecutter.project_slug}}.users.services.user_activation.send_email")

        endpoint = reverse("api:activation_request")

        request_data = {
            "email": inactive_user.email,
        }

        response = api_client.post(endpoint, data=request_data)

        assert response.status_code == status.HTTP_200_OK
        assert len(UserToken.objects.valid_tokens()) == 1
        assert mock_send_email.call_count == 1

    def test_user_activation_request_on_active_user(
            self, user: User, api_client: APIClient):
        endpoint = reverse("api:activation_request")

        request_data = {
            "email": user.email,
        }

        response = api_client.post(endpoint, data=request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert len(UserToken.objects.valid_tokens()) == 0

    def test_user_activation_request_on_non_existent_user(self, api_client: APIClient):
        endpoint = reverse("api:activation_request")

        request_data = {
            "email": "not-existing@test.com",
        }

        response = api_client.post(endpoint, data=request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert len(UserToken.objects.valid_tokens()) == 0

    def test_user_activation_confirm(
        self, inactive_user: User, api_client: APIClient, mocker):

        mock_send_email = mocker.patch(
            "{{cookiecutter.project_slug}}.users.services.user_activation.send_email")

        endpoint = reverse("api:activation_request")

        request_data = {
            "email": inactive_user.email,
        }

        response = api_client.post(endpoint, data=request_data)
        token = UserToken.objects.valid_tokens().first().token

        request_data = {
            "token": token,
            "password": TEST_P,
        }

        endpoint = reverse("api:activation_confirm")

        response = api_client.post(endpoint, data=request_data)

        assert response.status_code == status.HTTP_200_OK
        assert UserToken.objects.filter(token=token).first().used
        assert mock_send_email.call_count == 2

    def test_user_activation_confirm_invalid_token(
            self, user: User, api_client: APIClient):
        request_data = {
            "token": uuid.uuid4(),
            "password": TEST_P,
        }

        endpoint = reverse("api:activation_confirm")

        response = api_client.post(endpoint, data=request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPasswordReset:

    def test_user_password_reset_request(
            self, user: User, api_client: APIClient, mocker):

        mock_send_email = mocker.patch(
            "{{cookiecutter.project_slug}}.users.services.password_reset.send_email")

        endpoint = reverse("api:password_reset_request")

        request_data = {
            "email": user.email,
        }

        response = api_client.post(endpoint, data=request_data)

        assert response.status_code == status.HTTP_200_OK
        assert len(UserToken.objects.valid_tokens()) == 1
        assert mock_send_email.call_count == 1

    def test_user_password_reset_request_on_inactive_user(
            self, inactive_user: User, api_client: APIClient):
        endpoint = reverse("api:password_reset_request")

        request_data = {
            "email": inactive_user.email,
        }

        response = api_client.post(endpoint, data=request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert len(UserToken.objects.valid_tokens()) == 0

    def test_user_password_reset_request_on_non_existent_user(
            self, api_client: APIClient):
        endpoint = reverse("api:password_reset_request")

        request_data = {
            "email": "not-existing@test.com",
        }

        response = api_client.post(endpoint, data=request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert len(UserToken.objects.valid_tokens()) == 0

    def test_user_password_reset_confirm(
            self, user: User, api_client: APIClient, mocker):

        mock_send_email = mocker.patch(
            "{{cookiecutter.project_slug}}.users.services.password_reset.send_email")

        endpoint = reverse("api:password_reset_request")

        request_data = {
            "email": user.email,
        }

        response = api_client.post(endpoint, data=request_data)
        token = UserToken.objects.valid_tokens().first().token

        request_data = {
            "token": token,
            "password": TEST_P,
        }

        endpoint = reverse("api:password_reset_confirm")

        response = api_client.post(endpoint, data=request_data)

        assert response.status_code == status.HTTP_200_OK
        assert UserToken.objects.filter(token=token).first().used
        assert mock_send_email.call_count == 2


    def test_user_password_reset_confirm_invalid_token(
            self, user: User, api_client: APIClient):
        request_data = {
            "token": uuid.uuid4(),
            "password": TEST_P,
        }

        endpoint = reverse("api:password_reset_confirm")

        response = api_client.post(endpoint, data=request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
