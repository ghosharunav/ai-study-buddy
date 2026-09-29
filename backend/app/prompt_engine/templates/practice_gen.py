"""
PROMPT ENGINEERING LAYER — Practice Question Generator
=========================================================
Zero-shot + structured prompting, same pattern as the explainer, applied to
a new domain: open-ended (short-answer/conceptual) questions rather than MCQ.

Each question ships with an "ideal_answer_points" self-check checklist
instead of a single model answer — this is deliberate: for open-ended
questions there's no one correct phrasing to hide, and the checklist itself
is useful study material, not a spoiler.

Also includes the feedback prompt used when a student submits a written
answer for AI evaluation against that checklist.
"""

from app.prompt_engine.prompt_builder import build_role_instruction


def build_practice_questions_prompt(subject: str, topic: str, difficulty_level: str,
                                     num_questions: int) -> tuple[str, str]:
    system_instruction = build_role_instruction(subject, difficulty_level)

    prompt = f"""Generate {num_questions} open-ended practice questions (short-answer or conceptual — NOT multiple-choice) to help a student practice "{topic}" within {subject}, at the '{difficulty_level}' level.

For each question, also provide a short checklist of the key points a strong answer should cover. This lets the student self-check without being handed a single "model answer" to copy.

Respond with ONLY a single valid JSON object matching EXACTLY this structure:

{{
  "topic": "{topic}",
  "difficulty_level": "{difficulty_level}",
  "questions": [
    {{
      "question": "...",
      "ideal_answer_points": ["key point a strong answer should mention", "..."],
      "topic_tag": "a short 2-4 word sub-topic label"
    }}
  ]
}}

Rules:
- Exactly {num_questions} questions.
- Questions should require explanation or reasoning, not single-fact recall (avoid yes/no questions).
- 2 to 4 ideal_answer_points per question.
- Keep the JSON strictly valid: double quotes, no trailing commas."""

    return system_instruction, prompt


def build_feedback_prompt(subject: str, question: str, ideal_answer_points: list[str],
                           student_answer: str) -> tuple[str, str]:
    system_instruction = (
        f"You are Aria, an expert, encouraging {subject} tutor giving feedback on a "
        "student's practice answer. Be honest about gaps but always constructive and "
        "specific — point to exactly what's missing rather than just saying 'wrong'."
    )
    points_block = "\n".join(f"- {p}" for p in ideal_answer_points)

    prompt = f"""Question asked: "{question}"

Key points a strong answer should cover:
{points_block}

Student's answer:
\"\"\"{student_answer}\"\"\"

Evaluate the student's answer against the key points above.

Respond with ONLY a single valid JSON object matching EXACTLY this structure:

{{
  "covered_points": ["key points from the list above that the student's answer DID address"],
  "missed_points": ["key points from the list above that the student's answer did NOT address"],
  "overall_feedback": "2-4 sentences of specific, constructive feedback",
  "score_estimate": 0
}}

score_estimate is an integer 0-100, roughly proportional to how many key points were covered and how well. Keep the JSON strictly valid."""

    return system_instruction, prompt
