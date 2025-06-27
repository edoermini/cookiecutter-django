from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from {{ cookiecutter.project_slug }}.users.serializers.token import CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer



class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for token obtain
    """
    serializer_class = CustomTokenObtainPairSerializer

    def handle_exception(self, exc):
        return super().handle_exception(
            AuthenticationFailed("No active account found with the given credentials"),
        )


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom view for token refresh
    """
    serializer_class = CustomTokenRefreshSerializer
