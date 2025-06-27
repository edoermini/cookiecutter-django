from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from .views.password_reset import UserPasswordResetConfirmView
from .views.password_reset import UserPasswordResetRequestView
from .views.token import CustomTokenObtainPairView
from .views.token import CustomTokenRefreshView
from .views.user import UserViewSet
from .views.user_activation import UserActivationConfirmView
from .views.user_activation import UserActivationRequestView

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)

urlpatterns = [
    path('token/<int:app_id>/', CustomTokenObtainPairView.as_view(), name='token_obtain_app'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('activation/request/', UserActivationRequestView.as_view(), name='activation-request'),
    path('activation/confirm/', UserActivationConfirmView.as_view(), name='activation-confirm'),
    path('reset-password/request/', UserPasswordResetRequestView.as_view(), name='password-reset-request'),
    path('reset-password/confirm/', UserPasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]

urlpatterns += router.urls