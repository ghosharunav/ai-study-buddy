"""
Weak-topic detection and adaptive difficulty are deliberately NOT LLM calls.

They're a straightforward aggregation over data the app already has (every
quiz attempt's per-question results — see QuizAttempt.results_json). Reaching
for an LLM call here would be slower, less reliable, and strictly worse than
just... counting. This is the kind of engineering judgment worth calling out
explicitly in a project report: not everything in an "AI-powered app" needs
to be an AI call.
"""

import json

from sqlalchemy.orm import Session

from app.services.session_service import get_session_or_raise

WEAK_TOPIC_ACCURACY_THRESHOLD = 60.0  # a topic below this accuracy is "weak"
MAX_WEAK_TOPICS_RETURNED = 5


def compute_session_progress(db: Session, session_id: int) -> dict:
    session = get_session_or_raise(db, session_id)

    all_attempts = [attempt for quiz in session.quizzes for attempt in quiz.attempts]

    total_quizzes_taken = len(all_attempts)
    total_questions = sum(a.total for a in all_attempts)
    total_correct = sum(a.score for a in all_attempts)
    overall_accuracy = (
        round(100 * total_correct / total_questions, 1) if total_questions else None
    )

    # Aggregate per-topic accuracy across EVERY attempt in this session
    topic_stats: dict[str, dict[str, int]] = {}
    for attempt in all_attempts:
        for result in json.loads(attempt.results_json):
            tag = result["topic_tag"]
            stats = topic_stats.setdefault(tag, {"attempts": 0, "correct": 0})
            stats["attempts"] += 1
            if result["is_correct"]:
                stats["correct"] += 1

    topic_mastery = [
        {
            "topic_tag": tag,
            "attempts": stats["attempts"],
            "correct": stats["correct"],
            "accuracy": round(100 * stats["correct"] / stats["attempts"], 1),
        }
        for tag, stats in topic_stats.items()
    ]
    topic_mastery.sort(key=lambda t: t["accuracy"])  # weakest topics first

    weak_topics = [
        t["topic_tag"] for t in topic_mastery
        if t["accuracy"] < WEAK_TOPIC_ACCURACY_THRESHOLD
    ][:MAX_WEAK_TOPICS_RETURNED]

    # Simple rule-based adaptive difficulty suggestion
    suggested_difficulty = None
    if overall_accuracy is not None:
        if overall_accuracy >= 85:
            suggested_difficulty = "advanced"
        elif overall_accuracy <= 50:
            suggested_difficulty = "beginner"
        else:
            suggested_difficulty = "intermediate"

    return {
        "session_id": session.id,
        "subject": session.subject,
        "current_difficulty": session.difficulty_level,
        "total_quizzes_taken": total_quizzes_taken,
        "total_questions_answered": total_questions,
        "overall_accuracy": overall_accuracy,
        "topic_mastery": topic_mastery,
        "weak_topics": weak_topics,
        "suggested_difficulty": suggested_difficulty,
    }
