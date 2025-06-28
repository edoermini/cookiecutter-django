from django.contrib.auth.models import Permission
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from {{ cookiecutter.project_slug }}.users.models import User

from .exceptions import UserAlreadyExistsError


class UserSerializer(serializers.ModelSerializer[User]):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "last_login", "is_superuser",
                  "email", "password", "first_name", "last_name",
                  "is_staff", "is_active", "date_joined",
                  "groups", "apps", "permissions"]

    def get_permissions(self, obj):
        user_permissions = obj.user_permissions.all()
        group_permissions = Permission.objects.filter(group__user=obj)

        all_permissions = user_permissions | group_permissions
        return all_permissions.values_list("codename", flat=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation.update({
            "permissions": list(representation["permissions"]),
        })

        return representation

    def validate_email(self, value):
        """
        Check that the email is not already in use by another user.
        Also check that the email (which will be used as username)
        is not already in use.
        """
        user = self.context["request"].user

        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise UserAlreadyExistsError

        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise UserAlreadyExistsError

        return value

class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def validate_email(self, value):
        """
        Check that the email is not already in use by another user.
        Also check that the email (which will be used as username)
        is not already in use.
        """
        user = self.context["request"].user

        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise UserAlreadyExistsError

        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise UserAlreadyExistsError

        return value
