import logging
import time
from collections.abc import Callable
from typing import Any

from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.ai.base import AIProviderError, T

logger = logging.getLogger(__name__)

BATCH_SIZE = 32
MAX_ATTEMPTS = 3
RETRYABLE_CODES = {429, 500, 503}


def friendly_message(code: int | None) -> str:
    if code == 429:
        return "The AI service is busy or its usage limit was reached. Please try again."
    if code in (400, 401, 403):
        return "The AI service is not configured correctly."
    if code is not None and code >= 500:
        return "The AI service is temporarily unavailable. Please try again."
    return "The AI service could not process the request."


class GeminiProvider:
    def __init__(
        self,
        *,
        api_key: str,
        llm_model: str,
        embedding_model: str,
        embedding_dimensions: int,
    ) -> None:
        self.api_key = api_key
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.embedding_dimensions = embedding_dimensions
        self.client: genai.Client | None = None

    def _get_client(self) -> genai.Client:
        if not self.api_key:
            raise AIProviderError(
                "The AI service is not configured. Set GEMINI_API_KEY on the server."
            )

        if self.client is None:
            self.client = genai.Client(api_key=self.api_key)

        return self.client

    def _call(self, operation: Callable[[], Any]) -> Any:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                return operation()
            except errors.APIError as exc:
                if exc.code in RETRYABLE_CODES and attempt < MAX_ATTEMPTS:
                    delay = 2**attempt
                    logger.warning(
                        "Gemini API error %s; retrying in %s seconds",
                        exc.code,
                        delay,
                    )
                    time.sleep(delay)
                    continue

                logger.error("Gemini API error %s: %s", exc.code, exc)
                raise AIProviderError(friendly_message(exc.code)) from exc
            except AIProviderError:
                raise
            except Exception as exc:
                logger.exception("Unexpected error calling Gemini")
                raise AIProviderError(
                    "Could not reach the AI service."
                ) from exc

        raise AIProviderError("The AI service could not process the request.")

    def _embed(self, texts: list[str]) -> list[list[float]]:
        client = self._get_client()
        vectors: list[list[float]] = []

        for start in range(0, len(texts), BATCH_SIZE):
            batch = texts[start : start + BATCH_SIZE]

            # One Content object per input gives one embedding per text.
            contents = [
                types.Content(
                    parts=[types.Part.from_text(text=text)]
                )
                for text in batch
            ]

            response = self._call(
                lambda contents=contents: client.models.embed_content(
                    model=self.embedding_model,
                    contents=contents,
                    config=types.EmbedContentConfig(
                        output_dimensionality=self.embedding_dimensions,
                    ),
                )
            )

            embeddings = response.embeddings or []
            if len(embeddings) != len(batch):
                raise AIProviderError(
                    "The AI service returned an unexpected number of embeddings."
                )

            for item in embeddings:
                if (
                    item.values is None
                    or len(item.values) != self.embedding_dimensions
                ):
                    raise AIProviderError(
                        "The AI service returned an embedding of the wrong size."
                    )

                vectors.append(list(item.values))

        return vectors

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed(
            [f"title: none | text: {text}" for text in texts]
        )

    def embed_query(self, text: str) -> list[float]:
        return self._embed(
            [f"task: question answering | query: {text}"]
        )[0]

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: type[T],
    ) -> T:
        client = self._get_client()

        response = self._call(
            lambda: client.models.generate_content(
                model=self.llm_model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )
        )

        if not response.text:
            raise AIProviderError("The AI service returned an empty answer.")

        try:
            return schema.model_validate_json(response.text)
        except ValidationError as exc:
            logger.warning("Gemini returned invalid structured output: %s", exc)
            raise AIProviderError(
                "The AI service returned an answer in an unexpected format."
            ) from exc