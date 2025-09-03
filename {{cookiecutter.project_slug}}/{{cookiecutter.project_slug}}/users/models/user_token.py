import uuid
from typing import ClassVar

from django.db.models import CASCADE
from django.db.models import BooleanField
from django.db.models import DateTimeField
from django.db.models import ForeignKey
from django.db.models import Model
from django.db.models import PositiveSmallIntegerField
from django.db.models import UUIDField

from {{cookiecutter.project_slug}}.users.managers import UserTokenManager
from {{cookiecutter.project_slug}}.users.models.enums import TokenTypes

from . import User


class UserToken(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    token = UUIDField(default=uuid.uuid4, unique=True)
    token_type = PositiveSmallIntegerField(choices=TokenTypes.choices(), null=False)
    created_at = DateTimeField(auto_now_add=True)
    used = BooleanField(default=False)

    objects: ClassVar[UserTokenManager] = UserTokenManager()

    def __str__(self):
        return f"{self.user.email} - {self.token_type}"
