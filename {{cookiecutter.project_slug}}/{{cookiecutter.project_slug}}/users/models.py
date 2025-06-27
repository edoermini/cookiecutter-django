import uuid
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db.models import CASCADE
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import EmailField
from django.db.models import ForeignKey
from django.db.models import IntegerChoices
from django.db.models import Model
from django.db.models import PositiveSmallIntegerField
from django.db.models import UUIDField
from django.utils.translation import gettext_lazy as _

from .managers import UserManager
from .managers import UserTokenManager


class TokenTypes(IntegerChoices):
    ACTIVATION = 0, "User Activation"
    PASSWORD_RESET = 1, "Password Reset"

class User(AbstractUser):
    """
    Default custom user model for {{cookiecutter.project_name}}.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]

    email = EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

class UserToken(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    token = UUIDField(default=uuid.uuid4, unique=True)
    token_type = PositiveSmallIntegerField(choices=TokenTypes.choices, null=False)
    created_at = DateTimeField(auto_now_add=True)
    used = BooleanField(default=False)

    objects: ClassVar[UserTokenManager] = UserTokenManager()

    def __str__(self):
        return f"{self.user.email} - {self.token_type}"
