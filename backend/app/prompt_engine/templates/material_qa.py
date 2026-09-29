"""
PROMPT ENGINEERING LAYER — Chat With Your Material (RAG-lite)
=================================================================
CONTEXT-AWARE PROMPTING applied to retrieved document excerpts instead of
chat history: utils/retrieval.py picks the most relevant chunks from the
student's uploaded material, and this template injects them as labeled,
numbered excerpts, with an explicit instruction to answer ONLY from them
and say so honestly if the answer isn't there.

Structured output (grounded: bool) makes "I don't know" a first-class,
machine-checkable outcome instead of the model quietly hallucinating an
answer that sounds confident either way.
"""


def build_material_qa_prompt(subject: str, difficulty_level: str,
                              retrieved_chunks: list[tuple[int, str]],
                              question: str) -> tuple[str, str]:
    system_instruction = (
        f"You are Aria, an expert {subject} tutor helping a student at a "
        f"'{difficulty_level}' level understand THEIR OWN uploaded study material. "
        "You must answer using ONLY the excerpts provided below — never use "
        "outside knowledge to fill gaps, even if you know the answer generally. "
        "If the excerpts don't contain the answer, say so honestly rather than guessing."
    )

    excerpts_block = "\n\n".join(
        f"[Excerpt {i}]\n{chunk}" for i, chunk in retrieved_chunks
    )

    prompt = f"""Here are the most relevant excerpts from the student's uploaded material:

{excerpts_block}

Student's question: "{question}"

Respond with ONLY a single valid JSON object matching EXACTLY this structure:

{{
  "answer": "your answer, grounded strictly in the excerpts above",
  "grounded": true,
  "source_chunk_indices": [0, 2]
}}

Rules:
- "grounded" is true only if the excerpts actually contain enough information to answer the question. If they don't, set it to false and let "answer" honestly say the material doesn't cover this.
- "source_chunk_indices" lists the excerpt numbers you actually used to answer.
- Keep the JSON strictly valid: double quotes, no trailing commas."""

    return system_instruction, prompt
