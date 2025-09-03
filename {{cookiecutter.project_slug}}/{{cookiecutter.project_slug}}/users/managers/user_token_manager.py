from datetime import timedelta

from django.conf import settings
from django.db.models import Manager
from django.utils import timezone


class UserTokenManager(Manager):
    """Custom manager for UserToken model"""

    def valid_tokens(self):
        """Returns all the unused and not expired tokens"""
        expiry_threshold = timezone.now() - timedelta(hours=settings.TOKEN_EXPIRY_HOURS)
        return self.filter(used=False, created_at__gte=expiry_threshold)
