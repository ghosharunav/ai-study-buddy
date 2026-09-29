"""
FEW-SHOT PROMPTING — example library for the quiz generator.

Why few-shot for quizzes specifically (and not the explainer, which is
zero-shot): MCQ quality has failure modes that are hard to describe in
words but easy to demonstrate — plausible-but-not-silly distractors,
a difficulty level that actually matches the label, and explanations
that teach rather than just restate the answer. Showing 1-2 examples
steers the model far more reliably than instructions alone.

Deliberately from UNRELATED subjects (arithmetic, algorithms) — these
exist purely to demonstrate FORMAT and QUALITY BAR, not content for the
model to reuse. The prompt template makes this explicit to the model too.
"""

FEW_SHOT_QUIZ_EXAMPLES = [
    {
        "difficulty_level": "beginner",
        "example": {
            "question": "What is 5 + 3?",
            "options": ["6", "7", "8", "9"],
            "correct_answer_index": 2,
            "explanation": "5 + 3 equals 8 — starting at 5 and counting up three more: 6, 7, 8.",
            "topic_tag": "basic-arithmetic",
        },
    },
    {
        "difficulty_level": "advanced",
        "example": {
            "question": "Which sorting algorithm guarantees O(n log n) worst-case time but is not in-place?",
            "options": ["Quicksort", "Merge Sort", "Bubble Sort", "Insertion Sort"],
            "correct_answer_index": 1,
            "explanation": (
                "Merge Sort guarantees O(n log n) even in the worst case, but needs "
                "O(n) extra space for merging, so it isn't in-place. Quicksort is "
                "in-place but degrades to O(n^2) in the worst case."
            ),
            "topic_tag": "sorting-algorithms",
        },
    },
]
