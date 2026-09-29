from openai import OpenAI

from app.config import settings
from app.providers.base_provider import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is missing. Add it to your backend/.env file."
            )
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model_name = settings.openai_model

    @property
    def provider_name(self) -> str:
        return "openai"

    def generate(self, prompt: str, system_instruction: str | None = None,
                 temperature: float = 0.7, max_tokens: int = 1024) -> str:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
