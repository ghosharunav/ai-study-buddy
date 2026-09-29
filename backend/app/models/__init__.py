"""
Importing the model classes here (even though nothing below uses them
directly) is what makes SQLAlchemy aware of them, so that
Base.metadata.create_all(engine) in main.py actually creates these tables.
"""

from app.models.session import StudySession
from app.models.message import Message
from app.models.note import Note
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.summary import Summary
from app.models.practice_set import PracticeQuestionSet
from app.models.flashcard_set import FlashcardSet
from app.models.study_plan import StudyPlan
from app.models.study_material import StudyMaterial

__all__ = [
    "StudySession", "Message", "Note", "Quiz", "QuizAttempt",
    "Summary", "PracticeQuestionSet", "FlashcardSet", "StudyPlan", "StudyMaterial",
]
