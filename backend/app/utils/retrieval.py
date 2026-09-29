"""
RAG-LITE RETRIEVAL — no vector database, no embeddings API call.

Per the project's architecture decision (see docs/architecture notes): SQLite
is the database of record here, so rather than standing up a vector store for
a student project, retrieval is done with simple keyword overlap scoring.
This is a deliberate simplicity trade-off, not an oversight — it's fast, has
zero extra infrastructure, and is easy to explain and defend in a viva.

For a production system, this is exactly the piece you'd swap for embeddings
+ a vector index — the rest of the pipeline (chunk -> retrieve -> inject into
a grounded prompt -> validate structured output) stays the same either way.
"""

import re

_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "of", "to", "in", "on", "at", "for", "with", "by", "and", "or", "but",
    "what", "when", "where", "why", "how", "who", "which", "this", "that",
    "does", "do", "did", "can", "could", "would", "should", "will", "it",
    "its", "as", "from", "about",
}


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9']+", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


def keyword_retrieve(chunks: list[str], query: str, top_k: int = 3) -> list[tuple[int, str]]:
    """
    Scores each chunk by how many query keywords it contains, and returns
    the top_k highest-scoring chunks as (original_index, chunk_text) pairs,
    preserving their original order (not sorted by score) so the model sees
    them in the document's natural reading order.

    If every chunk scores 0 (no keyword overlap at all), falls back to the
    first top_k chunks rather than returning nothing — the model can still
    say "not found in the material" based on genuinely irrelevant context,
    which is more honest than silently returning zero context.
    """
    query_keywords = _keywords(query)
    scored = []
    for i, chunk in enumerate(chunks):
        chunk_keywords = _keywords(chunk)
        score = len(query_keywords & chunk_keywords)
        scored.append((i, chunk, score))

    top = sorted(scored, key=lambda x: x[2], reverse=True)[:top_k]

    if all(score == 0 for _, _, score in top):
        top = scored[:top_k]

    # Return in original document order, not score order — easier for the
    # model (and a human reader) to follow.
    top_indices = {i for i, _, _ in top}
    return [(i, chunk) for i, chunk in enumerate(chunks) if i in top_indices]
