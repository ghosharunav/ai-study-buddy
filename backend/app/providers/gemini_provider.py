from google import genai
from google.genai import types

from app.config import settings
from app.providers.base_provider import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing. Add it to your backend/.env file."
            )
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model_name = settings.gemini_model

    @property
    def provider_name(self) -> str:
        return "gemini"

    def generate(self, prompt: str, system_instruction: str | None = None,
                 temperature: float = 0.7, max_tokens: int = 1024) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                # temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        return response.text
