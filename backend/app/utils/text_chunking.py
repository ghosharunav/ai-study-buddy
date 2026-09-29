"""
Splits long text into chunks small enough to safely fit in one LLM call,
breaking on paragraph boundaries (and, as a fallback, sentence-ish
boundaries) rather than cutting mid-thought wherever possible.

Used by prompt_engine/chains/summarize_chain.py to implement map-reduce
summarization: long material gets chunked, each chunk summarized
individually (map), then all partial summaries combined into one
structured final summary (reduce).
"""


def chunk_text(text: str, max_chars: int = 6000) -> list[str]:
    """
    Returns a list of chunks, each at most ~max_chars long. If the whole
    text already fits, returns a single-element list (no unnecessary work).
    """
    text = text.strip()
    if len(text) <= max_chars:
        return [text]

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        if len(para) > max_chars:
            # A single paragraph is itself too big — flush what we have,
            # then hard-split this paragraph on sentence-ish boundaries.
            if current:
                chunks.append(current.strip())
                current = ""
            chunks.extend(_split_long_paragraph(para, max_chars))
            continue

        if len(current) + len(para) + 2 > max_chars:
            chunks.append(current.strip())
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para

    if current:
        chunks.append(current.strip())

    return chunks


def _split_long_paragraph(paragraph: str, max_chars: int) -> list[str]:
    """Fallback for a single paragraph too large to fit in one chunk on its own."""
    # crude sentence splitter — good enough for chunking purposes, not
    # meant to be a real NLP sentence tokenizer
    for punct in [". ", "? ", "! "]:
        paragraph = paragraph.replace(punct, punct[0] + "|")
    sentences = paragraph.split("|")

    chunks = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 > max_chars:
            if current:
                chunks.append(current.strip())
            current = sentence
        else:
            current = f"{current} {sentence}" if current else sentence

    if current:
        chunks.append(current.strip())

    return chunks
