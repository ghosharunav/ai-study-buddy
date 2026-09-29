"""
PROMPT ENGINEERING LAYER — Topic Explainer
============================================

Techniques demonstrated:

1. ZERO-SHOT PROMPTING
   No example explanations are shown to the model — we rely entirely on
   clear instructions and the model's own general knowledge. (Contrast this
   with the quiz generator in Phase 3, which uses FEW-SHOT prompting because
   MCQ format/difficulty calibration benefits much more from examples.)

2. STRUCTURED PROMPTING
   The exact JSON shape expected back is spelled out in the prompt itself,
   field by field — nothing is left to the model's discretion.

3. ROLE PROMPTING (reused, not re-implemented)
   The same tutor persona built in prompt_builder.py for the chat assistant
   is reused here. One persona per app, not a copy-pasted variant per feature.

This template works together with prompt_engine/chains/validated_generation.py,
which adds AI RESPONSE VALIDATION and PROMPT REFINEMENT on top of what's built here.
"""

from app.prompt_engine.prompt_builder import build_role_instruction


def build_explain_prompt(subject: str, topic: str, difficulty_level: str) -> tuple[str, str]:
    """
    Returns (system_instruction, prompt) ready for generate_validated_json().
    """
    system_instruction = build_role_instruction(subject, difficulty_level)

    task_prompt = f"""Explain the topic "{topic}" (within {subject}) to this student.

Respond with ONLY a single valid JSON object — no markdown code fences, no commentary before or after — matching EXACTLY this structure:

{{
  "topic": "{topic}",
  "difficulty_level": "{difficulty_level}",
  "summary": "a clear 2-3 sentence overview of the concept",
  "key_points": ["3 to 5 short bullet-point facts a student should remember"],
  "analogy": "one relatable, everyday analogy that makes this concept click",
  "common_mistakes": ["1 to 3 mistakes or misconceptions students often have about this topic"],
  "follow_up_questions": ["2 to 3 natural follow-up questions a curious student might ask next"]
}}

Keep the JSON strictly valid: use double quotes for all strings, no trailing commas, no comments."""

    return system_instruction, task_prompt
