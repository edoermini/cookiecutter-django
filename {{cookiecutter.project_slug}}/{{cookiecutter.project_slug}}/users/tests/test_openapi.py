import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

P = "password"

@pytest.fixture
def api_client():
    return APIClient()

def test_api_docs_accessible_by_admin(api_client, django_user_model):

    admin_user = django_user_model.objects.create_superuser(
        email="admin@example.com",
        password=P,
    )
    api_client.force_authenticate(user=admin_user)

    url = reverse("api-docs")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_api_docs_not_accessible_by_anonymous_users(api_client):
    url = reverse("api-docs")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_schema_generated_successfully(api_client, django_user_model):

    admin_user = django_user_model.objects.create_superuser(
        email="admin@example.com",
        password=P,
    )
    api_client.force_authenticate(user=admin_user)

    url = reverse("api-schema")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
