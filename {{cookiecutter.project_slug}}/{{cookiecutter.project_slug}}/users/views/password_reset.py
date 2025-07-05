from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from {{ cookiecutter.project_slug }}.users.models import User
from {{ cookiecutter.project_slug }}.users.serializers.password_reset import (
    UserPasswordResetConfirmSerializer,
)
from {{ cookiecutter.project_slug }}.users.serializers.password_reset import (
    UserPasswordResetRequestSerializer,
)
from {{ cookiecutter.project_slug }}.users.services.password_reset import PasswordResetService


class UserPasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        request_serializer = UserPasswordResetRequestSerializer(data=request.data)
        if request_serializer.is_valid():
            user_activation_service = PasswordResetService(
                user=User.objects.get(request_serializer.email),
            )

            user_activation_service.request()

            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

class UserPasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        request_serializer = UserPasswordResetConfirmSerializer(data=request.data)
        if request_serializer.is_valid():
            user_activation_service = PasswordResetService(
                user=User.objects.get(request_serializer.email),
                user_token=request_serializer.user_token,
            )

            user_activation_service.perform()

            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)
