from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from {{ cookiecutter.project_slug }}.users.serializers.user import UserSerializer
from {{ cookiecutter.project_slug }}.users.serializers.user import UserUpdateSerializer


class UserViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        """Return different serializers based on the action"""
        if self.action == "update_profile":
            return UserUpdateSerializer
        return UserSerializer

    @action(detail=False)
    def me(self, request):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=False, methods=["patch", "put"])
    def update_profile(self, request):
        """Update user information"""
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return the full user info after update
        return Response(UserSerializer(user).data)
