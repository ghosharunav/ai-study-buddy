from app.providers.base_provider import BaseLLMProvider
from app.prompt_engine.templates.study_plan import build_study_plan_prompt
from app.prompt_engine.output_schemas import StudyPlanOutput
from app.prompt_engine.chains.validated_generation import generate_validated_json


def generate_study_plan(
    provider: BaseLLMProvider, subject: str, difficulty_level: str,
    goal: str, weak_topics: list[str], num_days: int = 7,
) -> StudyPlanOutput:
    system_instruction, prompt = build_study_plan_prompt(subject, difficulty_level, goal, weak_topics, num_days)
    return generate_validated_json(
        provider=provider, system_instruction=system_instruction, prompt=prompt,
        schema=StudyPlanOutput, max_retries=1, temperature=0.6, max_tokens=2000,
    )
