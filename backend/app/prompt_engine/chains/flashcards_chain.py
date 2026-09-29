from app.providers.base_provider import BaseLLMProvider
from app.prompt_engine.templates.flashcards import build_flashcards_prompt
from app.prompt_engine.output_schemas import FlashcardSetOutput
from app.prompt_engine.chains.validated_generation import generate_validated_json


def generate_flashcards(
    provider: BaseLLMProvider, subject: str, topic: str,
    difficulty_level: str, num_cards: int = 10,
) -> FlashcardSetOutput:
    system_instruction, prompt = build_flashcards_prompt(subject, topic, difficulty_level, num_cards)
    return generate_validated_json(
        provider=provider, system_instruction=system_instruction, prompt=prompt,
        schema=FlashcardSetOutput, max_retries=1, temperature=0.6, max_tokens=1800,
    )
