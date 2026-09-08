import logging

from openai import OpenAI

from app.config import settings


logger = logging.getLogger(__name__)


class LLMClient:
    """Small wrapper around the OpenAI API."""

    def __init__(self):
        self.client = None

        if settings.openai_api_key:
            self.client = OpenAI(
                api_key=settings.openai_api_key,
                timeout=settings.llm_timeout_seconds,
                max_retries=settings.llm_max_retries,
            )

    def generate(self, user_message: str) -> str:
        """
        Generate an AI response.

        Returns a graceful fallback if the LLM is unavailable.
        """

        if not self.client:
            logger.warning("OpenAI API key is missing.")
            return self._fallback_response()

        try:
            response = self.client.responses.create(
                model=settings.llm_model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You are Mr.Shop, a helpful AI fashion stylist. "
                            "Give concise, practical fashion advice."
                        ),
                    },
                    {
                        "role": "user",
                        "content": user_message,
                    },
                ],
            )

            return response.output_text

        except Exception as exc:
            logger.exception("LLM request failed: %s", exc)
            return self._fallback_response()

    @staticmethod
    def _fallback_response() -> str:
        """Safe response when the LLM cannot be reached."""

        return (
            "I'm having trouble connecting to my AI service right now. "
            "Please try again in a moment."
        )


llm_client = LLMClient()