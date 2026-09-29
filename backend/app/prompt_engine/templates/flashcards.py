"""
PROMPT ENGINEERING LAYER — Flashcard Generator
=================================================
Zero-shot + structured prompting, same established pattern as the explainer
and practice-question generator, applied to a new output shape: simple
front/back flashcards for spaced repetition style review.
"""

from app.prompt_engine.prompt_builder import build_role_instruction


def build_flashcards_prompt(subject: str, topic: str, difficulty_level: str,
                             num_cards: int) -> tuple[str, str]:
    system_instruction = build_role_instruction(subject, difficulty_level)

    prompt = f"""Generate {num_cards} flashcards to help a student memorize and review key facts about "{topic}" within {subject}, at the '{difficulty_level}' level.

Each flashcard has a short "front" (a term, question, or prompt) and a concise "back" (the answer or definition) — keep both short enough to read at a glance, the way a real flashcard works.

Respond with ONLY a single valid JSON object matching EXACTLY this structure:

{{
  "topic": "{topic}",
  "difficulty_level": "{difficulty_level}",
  "cards": [
    {{
      "front": "a short term, question, or prompt",
      "back": "a concise answer or definition",
      "topic_tag": "a short 2-4 word sub-topic label"
    }}
  ]
}}

Rules:
- Exactly {num_cards} cards.
- Keep "front" under ~10 words and "back" under ~25 words — these are flashcards, not paragraphs.
- Cover distinct facts/sub-topics; avoid near-duplicate cards.
- Keep the JSON strictly valid: double quotes, no trailing commas."""

    return system_instruction, prompt
