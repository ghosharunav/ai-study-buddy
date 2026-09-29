"""
This is the CONTRACT every LLM provider must follow.

Why this matters for the project:
- The rest of the app (services, prompt engine) only ever talks to this
  interface, never to "Gemini" or "OpenAI" directly.
- Swapping providers later = writing one new class here, NOT touching
  any business logic, prompts, or routes.
"""

from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """Every concrete provider (Gemini, OpenAI, Claude) implements this."""

    @abstractmethod
    def generate(self, prompt: str, system_instruction: str | None = None,
                 temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """
        Send a prompt to the LLM and return the raw text response.

        Args:
            prompt: the full user/task prompt (already built by the prompt engine)
            system_instruction: role/persona instruction, kept separate from
                                 the task prompt so providers that support a
                                 dedicated system slot (all three do) use it properly
            temperature: creativity/randomness control
            max_tokens: cap on response length

        Returns:
            The model's raw text output (string). Callers that need JSON
            are responsible for parsing/validating it (see prompt_engine layer,
            built in Phase 2).
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Short identifier, e.g. 'gemini', 'openai', 'claude'. Used in logs/debug."""
        raise NotImplementedError
