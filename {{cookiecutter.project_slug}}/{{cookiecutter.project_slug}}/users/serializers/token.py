from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from .exceptions import UserNotActiveError
from .user import UserSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_active:
            raise UserNotActiveError
        
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        user_data = UserSerializer(user).data
        for key, value in user_data.items():
            token[key] = value
        return token

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    
    def validate(self, attrs):
        return super().validate(attrs)
