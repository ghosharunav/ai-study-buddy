"""
PROMPT ENGINEERING LAYER — Personalized Study Plan Generator
================================================================
This is CONTEXT-AWARE PROMPTING applied to real performance data, not just
chat history: the student's actual weak topics (computed from quiz_attempts —
see services/progress_service.py) are injected directly into the prompt, so
the generated plan is genuinely personalized rather than generic advice.

Weak-topic detection itself is deliberately NOT an LLM call (see
progress_service.py) — it's a straightforward aggregation over stored quiz
results. Only the plan's content generation uses the LLM. This is an
intentional engineering choice: don't reach for an LLM call where simple,
reliable, free computation already gives the right answer.
"""

from app.prompt_engine.prompt_builder import build_role_instruction


def build_study_plan_prompt(subject: str, difficulty_level: str, goal: str,
                             weak_topics: list[str], num_days: int) -> tuple[str, str]:
    system_instruction = build_role_instruction(subject, difficulty_level)

    if weak_topics:
        weak_topics_note = (
            f"This student's quiz history shows they specifically struggle with: "
            f"{', '.join(weak_topics)}. Prioritize these sub-topics, especially in "
            f"the earlier days of the plan."
        )
    else:
        weak_topics_note = (
            "No quiz performance data is available yet for this student, so build "
            "a well-rounded plan covering the subject's core sub-topics."
        )

    prompt = f"""Create a {num_days}-day personalized study plan for a student learning {subject} at the '{difficulty_level}' level.

Student's goal: "{goal}"

{weak_topics_note}

Respond with ONLY a single valid JSON object matching EXACTLY this structure:

{{
  "subject": "{subject}",
  "goal": "{goal}",
  "days": [
    {{
      "day_number": 1,
      "focus_topics": ["sub-topic(s) to focus on this day"],
      "activities": ["a concrete, specific study activity", "another one"],
      "estimated_minutes": 45
    }}
  ]
}}

Rules:
- Exactly {num_days} days, day_number from 1 to {num_days}.
- 2-4 activities per day, concrete and specific (not just 'study X' — say what to actually do: review notes, take a quiz, practice problems, etc).
- estimated_minutes between 15 and 120 per day, realistic for a student to actually complete.
- Keep the JSON strictly valid: double quotes, no trailing commas."""

    return system_instruction, prompt
