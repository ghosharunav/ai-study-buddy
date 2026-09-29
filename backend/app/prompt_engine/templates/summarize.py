"""
PROMPT ENGINEERING LAYER — Study Material Summarizer
======================================================
Demonstrates MAP-REDUCE style prompt chaining for long documents:
  MAP:    each chunk of the source text is summarized independently
          (zero-shot, plain text, told explicitly not to invent facts)
  REDUCE: all partial summaries (or the original text, if it was short
          enough to skip the map step) are combined into ONE structured,
          validated summary.
"""

from app.prompt_engine.prompt_builder import build_role_instruction


def build_chunk_summary_prompt(subject: str, chunk_text: str,
                                chunk_index: int, total_chunks: int) -> tuple[str, str]:
    """MAP step: a faithful, ungrounded-fact-free summary of one chunk."""
    system_instruction = (
        "You are Aria, an expert study assistant condensing raw material into "
        "faithful summaries. Never invent facts that are not present in the "
        "source text — if something is unclear, describe it as written rather "
        "than guessing."
    )
    prompt = f"""This is part {chunk_index + 1} of {total_chunks} of a longer piece of study material on {subject}.

Summarize ONLY the information in this part, in 3-6 concise sentences. Do not add outside knowledge or repeat information you'd expect to find in other parts — just summarize what's here.

--- MATERIAL (part {chunk_index + 1}/{total_chunks}) ---
{chunk_text}
--- END MATERIAL ---"""
    return system_instruction, prompt


def build_final_summary_prompt(subject: str, difficulty_level: str,
                                source_material: str, was_chunked: bool) -> tuple[str, str]:
    """REDUCE step: produces the final structured, validated summary."""
    system_instruction = build_role_instruction(subject, difficulty_level)

    source_note = (
        "The source material below is a set of partial summaries of a longer "
        "document — synthesize them into ONE coherent summary."
        if was_chunked else
        "The source material below is the student's original study material — "
        "summarize it faithfully, without adding outside information not "
        "present in the text."
    )

    prompt = f"""{source_note}

--- SOURCE MATERIAL ---
{source_material}
--- END SOURCE MATERIAL ---

Produce a study summary tailored for a student at the '{difficulty_level}' level.

Respond with ONLY a single valid JSON object matching EXACTLY this structure:

{{
  "title": "a short descriptive title for this material",
  "overview": "a 2-4 sentence high-level overview",
  "key_points": ["4 to 8 concise bullet-point facts from the material"],
  "important_terms": [
    {{"term": "...", "definition": "a one-sentence definition, grounded in the source material"}}
  ],
  "suggested_next_steps": ["1 to 3 suggestions for what the student should study or review next"]
}}

Only include information present in or directly implied by the source material — do not invent facts. Keep the JSON strictly valid: double quotes, no trailing commas."""

    return system_instruction, prompt
