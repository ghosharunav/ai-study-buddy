import anthropic

from app.config import settings
from app.providers.base_provider import BaseLLMProvider


class ClaudeProvider(BaseLLMProvider):
    def __init__(self):
        if not settings.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is missing. Add it to your backend/.env file."
            )
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model_name = settings.claude_model

    @property
    def provider_name(self) -> str:
        return "claude"

    def generate(self, prompt: str, system_instruction: str | None = None,
                 temperature: float = 0.7, max_tokens: int = 1024) -> str:
        response = self.client.messages.create(
            model=self.model_name,
            system=system_instruction or "",
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
