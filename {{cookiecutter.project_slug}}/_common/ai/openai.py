import io
import json
import logging
from dataclasses import dataclass

from openai import OpenAI
from openai.lib._parsing._completions import type_to_response_format_param
from pydantic import BaseModel

logger = logging.getLogger(__name__)

@dataclass
class BatchResult:
    """
    Encapsulates the result of retrieving an OpenAI batch job.

    Attributes:
        status (str): The batch job status (e.g., "completed", "failed").
        result_objects (list): Parsed result dictionaries from the batch output.
        batch_object (dict): Original batch metadata object from the OpenAI client.
        error (bool): True if an error occurred during retrieval or processing.
    """

    status: str
    result_objects: list
    batch_object: dict
    error: bool

@dataclass
class OpenAIMainConfig:
    """Configuration for `OpenAIMain`, the client interface for interacting with
    OpenAI's GPT chat models and batch APIs.

    Defines generation and sampling parameters to control model behavior for
    synchronous chat completions and batch processing.

    Attributes:
        model: The OpenAI model identifier to use for chat completions
            (e.g., "gpt-4o-preview", "gpt-4-turbo").
        temperature: Sampling temperature controlling randomness in the output.
            Lower values yield more deterministic outputs. Defaults to 0.1.
        top_p: Nucleus sampling parameter limiting the combined probability
            mass of considered tokens to control output diversity.
            Defaults to 1 (no restriction).
        frequency_penalty: Penalty applied to repeated tokens to reduce
            repetition in outputs. Defaults to 0.
        presence_penalty: Penalty encouraging the model to introduce new topics
            in the output. Higher values increase topic diversity. Defaults to 0.
    """

    model: str
    temperature: float = 0.1
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

class OpenAIMain:
    """
    Client interface for interacting with OpenAI's GPT chat models and batch APIs.

    Provides functionality to:
    - Perform synchronous chat completions with configurable parameters.
    - Create batch jobs from message objects for asynchronous processing.
    - Retrieve and parse OpenAI batch job results.

    Attributes:
        name (str): Name of this AI client instance (default "Transcribe").
        openai_client (OpenAI): OpenAI client instance initialized with the provided API key.
        model (str): OpenAI model used for completions (required).
        temperature (float): Sampling temperature controlling randomness in output.
            Defaults to 0.1.
        top_p (float): Nucleus sampling parameter for output diversity.
            Defaults to 1.
        frequency_penalty (float): Penalizes repeated tokens in output.
            Defaults to 0.
        presence_penalty (float): Encourages new topics in the output.
            Defaults to 0.

    Args:
        api_key (str):
            API key for authenticating with the OpenAI service.
        config (OpenAIMainConfig):
            A configuration dataclass specifying the model and generation parameters:
            - model (str): Identifier of the OpenAI model to use.
            - temperature (float, optional): Output randomness (default: 0.1).
            - top_p (float, optional): Nucleus sampling parameter (default: 1).
            - frequency_penalty (float, optional): Repetition penalty (default: 0).
            - presence_penalty (float, optional): Topic add penalty (default: 0).

    Usage:
        - Use `openai_client_chat_completions` for immediate chat completions.
        - Use `create_batch` to submit batch processing jobs.
        - Use `retrieve_batch` to fetch batch results.

    Note:
        Requires the OpenAI Python client.
        Batch processing relies on OpenAI's batch API endpoints.
    """

    __annotations__ = {}
    name = "Transcribe"

    def __init__(self,
                 api_key,
                 config : OpenAIMainConfig):

        self.openai_client = OpenAI(api_key=api_key)
        self.model = config.model
        self.temperature = config.temperature
        self.top_p = config.top_p
        self.frequency_penalty = config.frequency_penalty
        self.presence_penalty = config.presence_penalty

    def openai_client_chat_completions(
            self,
            messages: list[dict],
            response_format: BaseModel,
    ) -> dict:
        """
        Perform a synchronous chat completion request
        using the configured OpenAI client.

        Uses the current model and generation parameters (temperature, top_p,
        frequency_penalty, presence_penalty) to send a list of structured messages
        for immediate chat completion, returning the parsed structured JSON response.

        Args:
            messages (list[dict]): A list of message dictionaries formatted for OpenAI
                chat completions, typically containing system and user message entries.
            response_format (BaseModel): A Pydantic BaseModel indicating the expected
                structured response schema, used to inform the API of the desired
                output format.

        Returns:
            dict: Parsed JSON content returned from the chat completion response,
            structured according to the expected schema defined by the response format.

        Note:
            This method currently uses the `beta` chat completions endpoint. Consider
            migrating to the stable endpoint if your workloads do not require beta-only
            features.
        """

        # NOTE: Why are we using the beta?
        # The commercial release might be more appropriate.
        completion = self.openai_client.beta.chat.completions.parse(
            model=self.model,
            messages=messages,
            response_format=response_format,
            temperature=self.temperature,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
        )

        return json.loads(completion.choices[0].message.content)

    def _create_batch_from_file(self, file: io.BytesIO, metadata=None) -> str:
        """
        Creates a batch job from an input file using the OpenAI client.

        This method uploads a file to the OpenAI API for batch processing,
        then creates a batch job targeting the `/v1/chat/completions` endpoint.
        Optional metadata can be attached to the batch job for tracking or context.

        Args:
            file (io.BytesIO):
                A file-like object (in-memory bytes buffer) containing the batch
                input data.
                The file pointer will be reset to the beginning before upload.
            metadata (dict, optional):
                Optional metadata to associate with the batch job for
                additional context.
                Defaults to None.

        Returns:
            str:
                The ID of the created batch job.
        """

        file.seek(0)

        batch_file = self.openai_client.files.create(
            file=file,
            purpose="batch",
        )

        batch_job = self.openai_client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata=metadata,
        )

        return batch_job.id

    def create_batch(self,
                     objects: list,
                     response_format : BaseModel,
                     metadata : dict | None=None) -> str:
        """
        Creates a batch for OpenAPI processing.

        This method packages a list of conversation objects into a batch format,
        ensuring they conform to the specified Pydantic response model for structure
        and validation. Optionally, metadata can be attached to the batch for tracking
        or contextual use in downstream processing.

        Each object in `objects` should have the following structure:

            {
                "custom_id": str,
                "messages": list  # List of system/user messages, structured as needed
            }

        Args:
            objects (list of dict):
                A list of objects to include in the batch. Each object must contain:
                - `custom_id` (str): A unique identifier for the conversation.
                - `messages` (list): A list of message entries (system/user prompts).
            response_format (BaseModel):
                A Pydantic model defining the expected response schema for each object
                in the batch. Used for structure validation and serialization.
            metadata (dict, optional):
                Additional metadata to attach to the batch, such as tags or context.
                Defaults to None.

        Returns:
            str:
                The batch identifier or a confirmation message
                upon successful batch creation.

        Raises:
            ValidationError: If any object in `objects` does not conform to the provided
                `response_format`.
            ValueError: If required fields are missing in the provided objects.
        """

        if metadata is None:
            metadata = {}

        in_memory_file = io.BytesIO()

        for obj in objects:
            task = {
                "custom_id": obj["custom_id"],
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": self.model,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "frequency_penalty": self.frequency_penalty,
                    "presence_penalty": self.presence_penalty,
                    "response_format": type_to_response_format_param(response_format),
                    "messages": obj["messages"],
                },
            }
            line = (json.dumps(task) + "\n").encode("utf-8")
            in_memory_file.write(line)

        return self._create_batch_from_file(in_memory_file, metadata)

    def retrieve_batch(self, batch_id: str) -> BatchResult:
        """
        Retrieve the results and status of an OpenAI batch job by batch ID.

        Args:
            batch_id (str): The identifier of the OpenAI batch job.

        Returns:
            BatchResult: Encapsulates the result of retrieving an OpenAI batch job.
        """

        batch_object = self.openai_client.batches.retrieve(batch_id)
        result_objects = []
        error = False

        if batch_object.status == "completed":

            if batch_object.output_file_id:
                results = self.openai_client.files.content(batch_object.output_file_id)
                decoded_results = results.content.decode("utf-8")
                json_lines = decoded_results.strip().split("\n")

                for line in json_lines:
                    try:
                        completion = json.loads(line)
                        response_body = completion["response"]["body"]
                        content = response_body["choices"][0]["message"]["content"]

                        # Handle truncated or malformed JSON by
                        # ensuring it ends properly
                        if content.strip().endswith(","):
                            content = content.strip()[:-1] + "}"

                        data_analyzed = json.loads(content)
                        data_analyzed["custom_id"] = completion["custom_id"]
                        result_objects.append(data_analyzed)

                    except json.JSONDecodeError as e:
                        logger.warning("Error parsing JSON for line %s: %s", line, e)
                        continue

            elif batch_object.error_file_id:
                error = True

        elif batch_object.status in ["failed", "expired", "cancelled"]:
            error = True

        return BatchResult(
            status=batch_object.status,
            result_objects=result_objects,
            batch_object=batch_object,
            error=error,
        )
