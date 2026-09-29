"""
PROMPT ENGINEERING LAYER — Chat Assistant
==========================================

This module is deliberately isolated from routers/ and services/. Nothing
outside this file (and its siblings, added in later phases) should ever
hand-build a prompt string. That separation is the whole point of having
a "prompt engineering layer": prompts can be iterated on, evaluated, and
compared without touching business logic or API routes.

Techniques demonstrated here:

1. ROLE PROMPTING
   The system_instruction gives the model a persona ("expert, patient tutor")
   and constraints (adapt to difficulty level). This shapes tone and depth
   far more reliably than asking generically in the user prompt.

2. CONTEXT-AWARE PROMPTING
   Prior turns from the database are formatted back into the prompt so the
   model can refer to what was already discussed ("as I mentioned earlier...").
   We do this via explicit history injection into one text prompt rather than
   relying on any one provider's native multi-turn chat format — this keeps
   the BaseLLMProvider interface (Phase 0) simple and provider-agnostic:
   ANY provider that can take (system_instruction, prompt) can run this,
   no matter how its native API represents conversation turns.

3. STRUCTURED PROMPTING
   Even this "simple" chat prompt has an explicit structure (persona rules,
   then history, then the new turn, then a clear cue for where the model's
   reply begins) rather than being a free-form paragraph.

Later phases add: few-shot prompting (quiz generation), prompt chaining
(generate -> validate -> refine), and structured JSON output — each in its
own template file under prompt_engine/templates/.
"""

from app.models.message import Message

# How many prior turns to include. Keeps prompts small/cheap while still
# giving the model enough context to feel continuous. Tune this per subject
# if you want — it's a config knob, not a hardcoded assumption.
MAX_HISTORY_MESSAGES = 10


def build_role_instruction(subject: str, difficulty_level: str) -> str:
    """ROLE PROMPTING: defines who the model is being asked to act as."""
    difficulty_guidance = {
        "beginner": (
            "Use simple language, avoid jargon, and explain any technical term "
            "the first time you use it. Prefer short paragraphs and concrete "
            "everyday analogies over abstract definitions."
        ),
        "intermediate": (
            "You can use standard technical vocabulary for the subject, but "
            "still explain any non-obvious term. Balance conceptual explanation "
            "with a little more depth and nuance than a beginner explanation."
        ),
        "advanced": (
            "Assume strong foundational knowledge. Be precise and technical, "
            "get to the point quickly, and feel free to reference related "
            "advanced concepts, edge cases, or common misconceptions."
        ),
        "eli5": (
            "Explain this the way you'd explain it to a curious 5-year-old: "
            "very simple, playful words, short sentences, and a fun, concrete "
            "everyday comparison (toys, animals, food, family). Avoid technical "
            "terms entirely — if you must name one, immediately tie it to "
            "something a young child already knows."
        ),
    }.get(difficulty_level, "Adapt your explanation to the student's level.")

    return (
        f"You are Aria, an expert, patient, and encouraging AI tutor specializing "
        f"in {subject}. You are currently tutoring a student at a '{difficulty_level}' "
        f"level.\n\n"
        f"Teaching style rules:\n"
        f"- {difficulty_guidance}\n"
        f"- Keep responses focused and conversational — avoid overly long answers "
        f"unless the student is asking for deep detail.\n"
        f"- If the student seems confused, offer to re-explain differently rather "
        f"than repeating the same explanation.\n"
        f"- Stay strictly within the subject of {subject} unless the student "
        f"explicitly asks something unrelated."
    )


def _format_history(history: list[Message]) -> str:
    """Turns DB message rows into a plain-text transcript for the prompt."""
    if not history:
        return ""

    lines = []
    for msg in history[-MAX_HISTORY_MESSAGES:]:
        speaker = "Student" if msg.role == "user" else "Tutor"
        lines.append(f"{speaker}: {msg.content}")
    return "\n".join(lines)


def build_chat_prompt(
    subject: str,
    difficulty_level: str,
    history: list[Message],
    user_message: str,
) -> tuple[str, str]:
    """
    Builds a (system_instruction, prompt) pair ready to hand straight to
    any BaseLLMProvider.generate(...) call.

    Returns:
        system_instruction: the role-prompted persona/rules
        prompt: history transcript + the new student turn, ending with a
                clear cue for where the model should continue
    """
    system_instruction = build_role_instruction(subject, difficulty_level)
    history_text = _format_history(history)

    if history_text:
        prompt = f"{history_text}\nStudent: {user_message}\nTutor:"
    else:
        prompt = f"Student: {user_message}\nTutor:"

    return system_instruction, prompt
