import pytest

from django.urls import resolve
from django.urls import reverse

from {{ cookiecutter.project_slug }}.users.models import User


@pytest.fixture
def user(db):
    return User.objectrs.create_user(email="test@test.com", password="test1234_")

def test_user_me():
    assert reverse("api:users-me") == "/api/users/me/"
    assert resolve("/api/users/me/").view_name == "api:users-me"

def test_user_update():
    assert reverse("api:users-update-profile") == "/api/users/update_profile/"
    assert resolve("/api/users/update_profile/").view_name == "api:users-update-profile"

def test_token():
    assert reverse("api:token_obtain_pair") == "/api/token/"
    assert resolve("/api/token/").view_name == "api:token_obtain_pair"

def test_token_refresh():
    assert reverse("api:token_refresh") == "/api/token/reresh/"
    assert resolve("/api/token/refresh/").view_name == "api:token_refresh"

def test_user_activation_request():
    assert reverse("api:activation_request") == "/api/users/activation/request/"
    assert resolve("/api/users/activation/request/").view_name == "api:activation_request"

def test_user_activation_confirm():
    assert reverse("api:activation_confirm") == "/api/users/activation/confirm/"
    assert resolve("/api/users/activation/confirm/").view_name == "api:activation_confirm"

def test_user_password_reset_request():
    assert reverse("api:password_reset_request") == "/api/users/password-reset/request/"
    assert resolve("/api/users/password-reset/request/").view_name == "api:password_reset_request"

def test_user_password_reset_confirm():
    assert reverse("api:password_reset_confirm") == "/api/users/password-reset/confirm/"
    assert resolve("/api/users/password-reset/confirm/").view_name == "api:password_reset_confirm"
