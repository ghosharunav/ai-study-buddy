"""
PROMPT CHAINING — map-reduce summarization.

A third distinct chaining pattern in this codebase (compare to explain_chain's
single validate-retry, and quiz_chain's batch-then-selective-regenerate):

  MAP:    if the source text is long, split it into chunks (utils/text_chunking.py)
          and summarize each one independently — plain text, zero-shot, told
          explicitly not to invent facts.
  REDUCE: combine all partial summaries (or the raw text directly, if it was
          short enough that chunking was unnecessary) into ONE structured,
          schema-validated summary via the shared validated_generation chain.

Skipping the map step entirely for short text is a deliberate optimization —
no point spending extra LLM calls chunking something that already fits in
one request.
"""

from app.providers.base_provider import BaseLLMProvider
from app.utils.text_chunking import chunk_text
from app.prompt_engine.templates.summarize import build_chunk_summary_prompt, build_final_summary_prompt
from app.prompt_engine.output_schemas import SummaryOutput
from app.prompt_engine.chains.validated_generation import generate_validated_json


def summarize_material(
    provider: BaseLLMProvider,
    subject: str,
    difficulty_level: str,
    raw_text: str,
) -> SummaryOutput:
    chunks = chunk_text(raw_text, max_chars=6000)
    was_chunked = len(chunks) > 1

    if was_chunked:
        # MAP: summarize each chunk independently
        partial_summaries = []
        for i, chunk in enumerate(chunks):
            sys_i, prompt_i = build_chunk_summary_prompt(subject, chunk, i, len(chunks))
            partial = provider.generate(
                prompt=prompt_i, system_instruction=sys_i, temperature=0.4, max_tokens=400
            )
            partial_summaries.append(partial)
        source_material = "\n\n".join(
            f"[Part {i + 1}]\n{s}" for i, s in enumerate(partial_summaries)
        )
    else:
        source_material = chunks[0]

    # REDUCE: one structured, validated summary
    system_instruction, prompt = build_final_summary_prompt(
        subject, difficulty_level, source_material, was_chunked
    )
    return generate_validated_json(
        provider=provider,
        system_instruction=system_instruction,
        prompt=prompt,
        schema=SummaryOutput,
        max_retries=1,
        temperature=0.5,
        max_tokens=1200,
    )
