"""
Thin, feature-specific wrapper around the generic validated-generation chain.

Keeping this separate from validated_generation.py means each feature's
"chain" (its prompt template + its schema + any feature-specific tuning of
temperature/retries) lives in its own small, readable file, while the actual
retry/validation loop stays shared and consistent across all features.
"""

from app.providers.base_provider import BaseLLMProvider
from app.prompt_engine.templates.explain import build_explain_prompt
from app.prompt_engine.output_schemas import ExplanationOutput
from app.prompt_engine.chains.validated_generation import generate_validated_json


def generate_explanation(
    provider: BaseLLMProvider,
    subject: str,
    topic: str,
    difficulty_level: str,
) -> ExplanationOutput:
    system_instruction, prompt = build_explain_prompt(subject, topic, difficulty_level)
    return generate_validated_json(
        provider=provider,
        system_instruction=system_instruction,
        prompt=prompt,
        schema=ExplanationOutput,
        max_retries=1,
        temperature=0.6,
        max_tokens=1200,
    )
