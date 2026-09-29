"""
This is the ONLY place in the codebase that decides which concrete
provider class gets instantiated. Everything else asks this factory
for "the current provider" and doesn't care what's behind it.

To add a 4th provider later (e.g. local Llama, Mistral, etc.):
  1. Create providers/your_provider.py implementing BaseLLMProvider
  2. Add one line to _PROVIDERS below
That's it — no other file changes.
"""

from functools import lru_cache

from app.config import settings
from app.providers.base_provider import BaseLLMProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.claude_provider import ClaudeProvider

_PROVIDERS = {
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
    "claude": ClaudeProvider,
}


@lru_cache
def get_llm_provider() -> BaseLLMProvider:
    """
    Returns a cached instance of the active provider, chosen by
    LLM_PROVIDER in .env. Cached so we don't reconnect/reconfigure
    the SDK on every single request.
    """
    provider_key = settings.llm_provider.lower().strip()

    if provider_key not in _PROVIDERS:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider_key}'. "
            f"Valid options: {list(_PROVIDERS.keys())}"
        )

    provider_class = _PROVIDERS[provider_key]
    return provider_class()
