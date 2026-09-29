"""
PROMPT ENGINEERING LAYER — Quiz Generator
============================================

Techniques demonstrated:

1. FEW-SHOT PROMPTING
   Unlike the zero-shot explainer, we show the model 1-2 example questions
   (from unrelated subjects) before asking it to generate real ones. This
   steers format, difficulty calibration, and explanation quality far more
   reliably than instructions alone — see few_shot_examples/quiz_examples.py.

2. STRUCTURED PROMPTING
   The exact JSON shape (including per-question topic_tag, used later for
   weak-topic detection) is spelled out explicitly.

3. ROLE PROMPTING (reused)
   Same tutor persona as chat and the explainer.
"""

import json

from app.prompt_engine.prompt_builder import build_role_instruction
from app.prompt_engine.few_shot_examples.quiz_examples import FEW_SHOT_QUIZ_EXAMPLES


def _format_few_shot_block() -> str:
    lines = []
    for ex in FEW_SHOT_QUIZ_EXAMPLES:
        lines.append(f"Example (difficulty: {ex['difficulty_level']}):")
        lines.append(json.dumps(ex["example"], indent=2))
        lines.append("")
    return "\n".join(lines)


def build_quiz_prompt(subject: str, topic: str, difficulty_level: str,
                       num_questions: int = 5) -> tuple[str, str]:
    """Returns (system_instruction, prompt) for the full-batch quiz generation call."""
    system_instruction = build_role_instruction(subject, difficulty_level)
    few_shot_block = _format_few_shot_block()

    task_prompt = f"""Generate {num_questions} multiple-choice questions (MCQs) to test a student's understanding of "{topic}" within {subject}, at the '{difficulty_level}' difficulty level.

Here are examples of the exact question format and quality expected (these are from UNRELATED subjects — they only demonstrate format, difficulty calibration, and explanation style, not content to copy):

{few_shot_block}
Now generate your own {num_questions} original questions about "{topic}", following that same format and quality bar.

Respond with ONLY a single valid JSON object — no markdown fences, no commentary — matching EXACTLY this structure:

{{
  "topic": "{topic}",
  "difficulty_level": "{difficulty_level}",
  "questions": [
    {{
      "question": "...",
      "options": ["...", "...", "...", "..."],
      "correct_answer_index": 0,
      "explanation": "...",
      "topic_tag": "a short 2-4 word sub-topic label for this specific question"
    }}
  ]
}}

Rules:
- Exactly {num_questions} questions in the array.
- Each question has EXACTLY 4 distinct options.
- correct_answer_index is 0, 1, 2, or 3 and must point to the genuinely correct option.
- Distractors (wrong options) should be plausible, not silly or obviously wrong.
- Keep each explanation concise (1-2 sentences) but genuinely informative — it should teach, not just restate the answer.
- Keep the JSON strictly valid: double quotes for all strings, no trailing commas, no comments."""

    return system_instruction, task_prompt


def build_single_question_prompt(subject: str, topic: str, difficulty_level: str,
                                  existing_topic_tags: list[str]) -> tuple[str, str]:
    """
    Used by the quiz chain to regenerate ONE question that failed a deeper
    validation check, without discarding the rest of an otherwise-good batch.
    """
    system_instruction = build_role_instruction(subject, difficulty_level)
    avoid_tags = ", ".join(existing_topic_tags) if existing_topic_tags else "none yet"

    prompt = f"""Generate exactly ONE multiple-choice question to test a student's understanding of "{topic}" within {subject}, at the '{difficulty_level}' difficulty level.

Avoid duplicating these sub-topics already covered in this quiz: {avoid_tags}.

Respond with ONLY a single valid JSON object matching EXACTLY this structure:

{{
  "question": "...",
  "options": ["...", "...", "...", "..."],
  "correct_answer_index": 0,
  "explanation": "...",
  "topic_tag": "a short 2-4 word sub-topic label"
}}

All 4 options must be distinct, plausible, and exactly one must be correct."""

    return system_instruction, prompt
