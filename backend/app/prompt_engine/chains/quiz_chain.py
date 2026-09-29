"""
PROMPT CHAINING — a more elaborate version than the explainer's chain.

The explainer's chain (Phase 2) validates ONE JSON object and retries the
WHOLE thing if it's broken. That's wasteful for a quiz: if 4 out of 5
questions are great and 1 has a duplicate option, throwing away all 5 and
starting over wastes tokens and can make an otherwise-good batch worse.

So this chain does something more surgical:
  1. Generate the full batch (few-shot prompt) and validate the overall
     JSON shape via the generic generate_validated_json() chain.
  2. Run a deeper, semantic check on EACH question individually — things a
     Pydantic schema can't catch, like duplicate options or an empty string
     that technically satisfies "min_length=1" at the field level.
  3. Any question that fails step 2 gets regenerated INDIVIDUALLY (its own
     small prompt, its own validation), and only that question is replaced
     in the final list — the rest of the batch is untouched.

This is "prompt chaining" in the fullest sense: multiple prompts, each
doing a smaller job, composed together to produce a more reliable result
than any single call could.
"""

from app.providers.base_provider import BaseLLMProvider
from app.prompt_engine.templates.quiz_gen import build_quiz_prompt, build_single_question_prompt
from app.prompt_engine.output_schemas import QuizOutput, QuizQuestionOutput
from app.prompt_engine.chains.validated_generation import generate_validated_json


def _is_semantically_valid(q: QuizQuestionOutput) -> bool:
    """Checks the things a Pydantic schema alone can't: duplicate options,
    blank-ish text that technically passed schema validation."""
    if len(set(opt.strip().lower() for opt in q.options)) != 4:
        return False  # duplicate or near-duplicate options
    if not q.question.strip() or not q.explanation.strip():
        return False
    return True


def generate_quiz(
    provider: BaseLLMProvider,
    subject: str,
    topic: str,
    difficulty_level: str,
    num_questions: int = 5,
) -> QuizOutput:
    # Step 1: generate + validate the whole batch's JSON shape
    system_instruction, prompt = build_quiz_prompt(subject, topic, difficulty_level, num_questions)
    quiz: QuizOutput = generate_validated_json(
        provider=provider,
        system_instruction=system_instruction,
        prompt=prompt,
        schema=QuizOutput,
        max_retries=1,
        temperature=0.7,
        max_tokens=2500,
    )

    # Step 2 + 3: deeper per-question check, selective regeneration
    fixed_questions: list[QuizQuestionOutput] = []
    for q in quiz.questions:
        if _is_semantically_valid(q):
            fixed_questions.append(q)
            continue

        # This one question is bad — regenerate just this one, avoiding
        # sub-topics already covered by the good questions so far.
        existing_tags = [fq.topic_tag for fq in fixed_questions]
        single_system, single_prompt = build_single_question_prompt(
            subject, topic, difficulty_level, existing_tags
        )
        regenerated: QuizQuestionOutput = generate_validated_json(
            provider=provider,
            system_instruction=single_system,
            prompt=single_prompt,
            schema=QuizQuestionOutput,
            max_retries=1,
            temperature=0.7,
            max_tokens=600,
        )
        fixed_questions.append(regenerated)

    quiz.questions = fixed_questions
    return quiz
