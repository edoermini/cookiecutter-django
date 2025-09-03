from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db.models import EmailField
from django.utils.translation import gettext_lazy as _

from {{cookiecutter.project_slug}}.users.managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for {{cookiecutter.project_name}}.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    email = EmailField(_("email address"), unique=True)
    username=None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()
