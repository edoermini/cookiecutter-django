from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

from {{ cookiecutter.project_slug }}.users.serializers.token import CustomTokenObtainPairSerializer
from {{ cookiecutter.project_slug }}.users.serializers.token import CustomTokenRefreshSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for token obtain
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom view for token refresh
    """
    serializer_class = CustomTokenRefreshSerializer
    permission_classes = [AllowAny]
