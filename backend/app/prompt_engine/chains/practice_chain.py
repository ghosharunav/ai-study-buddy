"""
Feature-specific chain wrappers for the practice-question generator.
Both are thin — the real work is the shared generate_validated_json chain;
these just supply the right template + schema for each step.
"""

from app.providers.base_provider import BaseLLMProvider
from app.prompt_engine.templates.practice_gen import build_practice_questions_prompt, build_feedback_prompt
from app.prompt_engine.output_schemas import PracticeQuestionSetOutput, PracticeFeedbackOutput
from app.prompt_engine.chains.validated_generation import generate_validated_json


def generate_practice_questions(
    provider: BaseLLMProvider,
    subject: str,
    topic: str,
    difficulty_level: str,
    num_questions: int = 5,
) -> PracticeQuestionSetOutput:
    system_instruction, prompt = build_practice_questions_prompt(subject, topic, difficulty_level, num_questions)
    return generate_validated_json(
        provider=provider,
        system_instruction=system_instruction,
        prompt=prompt,
        schema=PracticeQuestionSetOutput,
        max_retries=1,
        temperature=0.7,
        max_tokens=2000,
    )


def get_practice_feedback(
    provider: BaseLLMProvider,
    subject: str,
    question: str,
    ideal_answer_points: list[str],
    student_answer: str,
) -> PracticeFeedbackOutput:
    system_instruction, prompt = build_feedback_prompt(subject, question, ideal_answer_points, student_answer)
    return generate_validated_json(
        provider=provider,
        system_instruction=system_instruction,
        prompt=prompt,
        schema=PracticeFeedbackOutput,
        max_retries=1,
        temperature=0.4,
        max_tokens=600,
    )
