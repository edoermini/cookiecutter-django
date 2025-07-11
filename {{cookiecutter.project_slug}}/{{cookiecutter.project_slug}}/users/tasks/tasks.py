import logging

from celery import shared_task

from _config.celery_app import app
from {{cookiecutter.project_slug}}.users.models import User

logger = logging.getLogger(__name__)

@shared_task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()

class GetUsersCount(app.Task):
    """A pointless Celery task class to demonstrate usage."""

    __annotations__ = {}
    name = "GetUsersCount"

    def run(self):
        get_users_count.apply_async(args=[], kwargs={"s": "-"}, task_id="12345")

GetUsersCount = app.register_task(GetUsersCount)
