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

router.register("users", UserViewSet, basename='users')

urlpatterns = [
    path("token/",
         CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/",
         CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("/users/activation/request/",
         UserActivationRequestView.as_view(), name="activation_request"),
    path("/users/activation/confirm/",
         UserActivationConfirmView.as_view(), name="activation_confirm"),
    path("/users/password-reset/request/",
         UserPasswordResetRequestView.as_view(), name="password_reset_request"),
    path("/users/password-reset/confirm/",
         UserPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
]

urlpatterns += router.urls
