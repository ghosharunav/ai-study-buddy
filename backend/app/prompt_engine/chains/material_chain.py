from app.providers.base_provider import BaseLLMProvider
from app.prompt_engine.templates.material_qa import build_material_qa_prompt
from app.prompt_engine.output_schemas import MaterialAnswerOutput
from app.prompt_engine.chains.validated_generation import generate_validated_json


def answer_from_material(
    provider: BaseLLMProvider, subject: str, difficulty_level: str,
    retrieved_chunks: list[tuple[int, str]], question: str,
) -> MaterialAnswerOutput:
    system_instruction, prompt = build_material_qa_prompt(subject, difficulty_level, retrieved_chunks, question)
    return generate_validated_json(
        provider=provider, system_instruction=system_instruction, prompt=prompt,
        schema=MaterialAnswerOutput, max_retries=1, temperature=0.3, max_tokens=800,
    )
