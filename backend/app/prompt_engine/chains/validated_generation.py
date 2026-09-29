"""
GENERIC PROMPT CHAIN: Generate -> Validate -> Refine
======================================================

This is the reusable "chain" every structured-output feature (explanations
now, quizzes/flashcards/study plans later) is built on top of. It demonstrates
three prompt-engineering techniques at once:

1. STRUCTURED JSON OUTPUT
   The LLM is asked to return JSON matching a specific schema — not free text
   we then try to regex apart.

2. AI RESPONSE VALIDATION
   We never trust the LLM's output blindly. It's parsed and validated against
   a Pydantic schema before anything is stored or shown to the user.

3. PROMPT CHAINING / REFINEMENT
   If validation fails, we don't just error out — we send the model its own
   broken output PLUS the exact validation error, and ask it to fix itself.
   This one extra round-trip fixes the vast majority of "almost-JSON"
   responses (a stray sentence before the '{', a trailing comma, a missing
   field) without any human ever seeing the failure.

Any new feature that needs structured JSON from the LLM should call
generate_validated_json(...) below rather than re-implementing this loop —
that's what keeps every feature's error handling and retry behavior consistent.
"""

import json
from pydantic import BaseModel, ValidationError

from app.providers.base_provider import BaseLLMProvider


class JSONGenerationError(Exception):
    """Raised when the LLM still can't produce valid JSON after all retries."""
    pass


def _strip_markdown_fences(text: str) -> str:
    """Models often wrap JSON in ```json ... ``` even when explicitly told not
    to — rather than fighting that in every prompt, we just handle it here."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def generate_validated_json(
    provider: BaseLLMProvider,
    system_instruction: str,
    prompt: str,
    schema: type[BaseModel],
    max_retries: int = 1,
    temperature: float = 0.6,
    max_tokens: int = 1500,
) -> BaseModel:
    """
    Calls the LLM, then validates its output against `schema`. If validation
    fails, retries up to `max_retries` times with a refinement prompt that
    shows the model exactly what went wrong.

    Returns a validated instance of `schema`.
    Raises JSONGenerationError if every attempt fails.
    """
    raw_output = provider.generate(
        prompt=prompt,
        system_instruction=system_instruction,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    attempt = 0
    last_error: Exception | None = None

    while attempt <= max_retries:
        try:
            cleaned = _strip_markdown_fences(raw_output)
            data = json.loads(cleaned)
            return schema.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            attempt += 1
            if attempt > max_retries:
                break

            refine_prompt = (
                "Your previous response was supposed to be ONLY a valid JSON "
                "object, but it failed to parse or didn't match the required "
                "structure.\n\n"
                f"--- Your previous output ---\n{raw_output}\n\n"
                f"--- Validation error ---\n{str(e)}\n\n"
                "Respond again with ONLY the corrected, valid JSON object. "
                "No markdown fences, no explanation, no text before or after "
                "the JSON."
            )
            raw_output = provider.generate(
                prompt=refine_prompt,
                system_instruction=system_instruction,
                temperature=0.2,  # lower temperature for the fix-it attempt: we want precision, not creativity
                max_tokens=max_tokens,
            )

    raise JSONGenerationError(
        f"Model failed to produce valid JSON after {max_retries + 1} attempt(s). "
        f"Last error: {last_error}"
    )
