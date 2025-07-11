import logging
import uuid

from _common.ai.openai import OpenAIMain
from _common.utils.decorators import no_simultaneous_execution
from _config.celery_app import app

from {{cookiecutter.project_slug}}.users.models import User
from {{cookiecutter.project_slug}}.users.pydantic_models import (
    UserNameDempgraphicAnalysisResponseModel,
)

logger = logging.getLogger(__name__)

class UsersNamesDemographicAnalysisUsingOpenAIBatchRequest(OpenAIMain, app.Task):
    """
    A pointless Celery task class which uses OpenAIMain
    class and it's create_batch method to demonstrate usage.
    """

    __annotations__ = {}
    name = "UsersNamesDemographicAnalysisUsingOpenAIBatchRequest"

    @no_simultaneous_execution(lock_expiration_time=600)
    def run(self, **kwargs):
        objects = []

        # Create system message with the available categories
        system_message = {
            "role": "system",
            "content": (
                "You are a Demographer. Analyze the users lists passed to you and \
                make a demographic analysis of each user in the list by \
                analyzing:\n"
                "1. How common is the name in the population giving a percentage\n"
                "2. How common is the surname in the population giving a percentage"
                "2. How common is the name among people of the same sex\n"
                "2. How common is the name among people of the same sex\n"
                "Note that each user within the list is identified as a tuple \
                containing name and surname"
            ),
        }

        # dummy objects list in which each object contains a request
        # with a list containing in turn one user
        objects = [
            {
                "custom_id": uuid.uuid4(),
                "messages": [
                    system_message,
                    {
                        "role": "user",
                        "content":
                            f"[({user.first_name}, {user.last_name})]",
                    },
                ],
            }
            for user in User.objects.all()
        ]

        # Create batch and retrieve results
        batch_id = self.create_batch(objects, UserNameDempgraphicAnalysisResponseModel)
        batch_result = self.retrieve_batch(batch_id)

        if batch_result.error:
            msg = "Batch processing failed or returned error results."
            raise RuntimeError(msg)

        total_count = 0

        for result in batch_result.result_objects:
            try:
                # Assuming UserCountResponseModel has an attribute `count`
                total_count += result.get("count", 0)
            except Exception as e:
                logger.warning("Failed to parse count from result %s: %s", result, e)
                continue

        return total_count

class UsersNamesDemographicAnalysisUsingOpenAIChatCompletion(OpenAIMain, app.Task):
    """
    A pointless Celery task class which uses OpenAIMain
    class and it's create_batch method to demonstrate usage.
    """

    __annotations__ = {}
    name = "UsersNamesDemographicAnalysisUsingOpenAIChatCompletion"

    @no_simultaneous_execution(lock_expiration_time=600)
    def run(self, **kwargs):

        # Create system message with the available categories
        system_message = {
            "role": "system",
            "content": (
                "You are a Demographer. Analyze the users lists passed to you and \
                make a demographic analysis of each user in the list by \
                analyzing:\n"
                "1. How common is the name in the population giving a percentage\n"
                "2. How common is the surname in the population giving a percentage"
                "2. How common is the name among people of the same sex\n"
                "2. How common is the name among people of the same sex\n"
                "Note that each user within the list is identified as a tuple \
                containing name and surname"
            ),
        }

        user = User.objects.first()
        # dummy objects list in which each object contains a request
        # with a list containing in turn one user
        messages = [
            system_message,
            {
                "role": "user",
                "content":
                    f"[({user.first_name}, {user.last_name})]",
            },
        ]

        return self.openai_client_chat_completions(
            messages,
            UserNameDempgraphicAnalysisResponseModel,
        )

UsersNamesDemographicAnalysisUsingOpenAIBatchRequest = \
    app.register_task(UsersNamesDemographicAnalysisUsingOpenAIBatchRequest)
UsersNamesDemographicAnalysisUsingOpenAIChatCompletion = \
    app.register_task(UsersNamesDemographicAnalysisUsingOpenAIChatCompletion)