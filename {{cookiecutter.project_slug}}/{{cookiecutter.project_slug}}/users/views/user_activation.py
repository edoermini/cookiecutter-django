from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from {{ cookiecutter.project_slug }}.users.models import User
from {{ cookiecutter.project_slug }}.users.serializers.user_activation import (
    UserActivationConfirmSerializer,
)
from {{ cookiecutter.project_slug }}.users.serializers.user_activation import (
    UserActivationRequestSerializer,
)
from {{ cookiecutter.project_slug }}.users.services.user_activation import UserActivationService


class UserActivationRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        request_serializer = UserActivationRequestSerializer(data=request.data)
        if request_serializer.is_valid():
            user_activation_service = UserActivationService()

            user_activation_service.request(
                user=User.objects.get(email=request_serializer.validated_data["email"]),
            )

            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

class UserActivationConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        request_serializer = UserActivationConfirmSerializer(data=request.data)
        if request_serializer.is_valid():
            user_activation_service = UserActivationService(
                user_token=request_serializer.validated_data["user_token"],
            )

            user_activation_service.perform(
                request_serializer.validated_data["password"],
            )

            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)
