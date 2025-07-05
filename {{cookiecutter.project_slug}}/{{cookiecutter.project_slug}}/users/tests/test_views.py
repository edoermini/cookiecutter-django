import pytest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import force_authenticate

from {{ cookiecutter.project_slug }}.users.models import User
from {{ cookiecutter.project_slug }}.users.serializers.user import UserSerializer
from {{ cookiecutter.project_slug }}.users.serializers.exceptions import UserAlreadyExistsError


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create(
        email="test@test.com",
        first_name="Test",
        last_name="Test",
        password="test1234_",
    )

@pytest.fixture
def user2(db):
    return User.objects.create(
        email="new-email@test.com",
        first_name="Test",
        last_name="Test",
        password="test1234_",
    )

class TestUserViewSet:

    def test_me_unauthorized(user: User, api_client: APIClient):
        endpoint = reverse("api:users-me")

        response = api_client.get(endpoint)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_me(user: User, api_client: APIClient):
        endpoint = reverse("api:users-me")

        api_client.force_authenticate(user=user)
        response = api_client.get(endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == UserSerializer(user).data
    
    def test_update_unauthorized(user: User, api_client: APIClient):
        endpoint = reverse("api:users-update-profile")

        response = api_client.put(endpoint)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_email_already_in_use(user: User, user2: User, api_client: APIClient):
        endpoint = reverse("api:users-update-profile")

        data = {"email": "new-email@test.com"}

        api_client.force_authenticate(user=user)
        response = api_client.put(endpoint, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
        assert response.data.get("email")[0] == UserAlreadyExistsError().detail[0]

    @pytest.mark.django_db
    def test_update(user: User, api_client: APIClient):
        endpoint = reverse("api:users-update-profile")

        data = {"email": "new-email@test.com"}

        api_client.force_authenticate(user=user)
        response = api_client.put(endpoint, data=data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("email") == data.get("email")


class TestToken:
    
    def test_obtain_token_pair(user: User, api_client: APIClient):
        endpoint = reverse('api:token_obtain_pair')

        data = {
            'email': user.email,
            'password': "test1234_"
        }

        response = api_client.post(endpoint, data=data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

        # testing accessing to restricted view

        access_token = response.data['access']

        response = api_client.get(reverse('api:users-me'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = api_client.get(reverse('api:users-me'))

        assert response.status_code == status.HTTP_200_OK
    
    def test_refresh_token_pair(user: User, api_client: APIClient):
        endpoint = reverse('api:refresh_token')

        api_client.force_authenticate(user=user)
        response = api_client.post(endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

        # testing accessing to restricted view

        access_token = response.data['access']

        response = api_client.get(reverse('api:users-me'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = api_client.get(reverse('api:users-me'))