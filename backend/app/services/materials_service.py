import json

from sqlalchemy.orm import Session

from app.models.study_material import StudyMaterial
from app.utils.text_chunking import chunk_text
from app.utils.retrieval import keyword_retrieve
from app.prompt_engine.chains.material_chain import answer_from_material
from app.providers.provider_factory import get_llm_provider
from app.services.session_service import get_session_or_raise


class MaterialNotFoundError(Exception):
    pass


def upload_material(db: Session, session_id: int, filename: str, raw_text: str) -> StudyMaterial:
    session = get_session_or_raise(db, session_id)
    # Smaller chunks than the summarizer uses (1500 vs 6000 chars) — retrieval
    # works better with more, smaller, topically-focused pieces to choose from.
    chunks = chunk_text(raw_text, max_chars=1500)

    material = StudyMaterial(
        session_id=session.id, filename=filename, chunks_json=json.dumps(chunks),
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


def list_materials(db: Session, session_id: int) -> list[StudyMaterial]:
    session = get_session_or_raise(db, session_id)
    return session.study_materials


def get_material_or_raise(db: Session, material_id: int) -> StudyMaterial:
    material = db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
    if material is None:
        raise MaterialNotFoundError(f"Study material {material_id} not found")
    return material


def ask_material(db: Session, material_id: int, question: str):
    material = get_material_or_raise(db, material_id)
    chunks = json.loads(material.chunks_json)
    retrieved = keyword_retrieve(chunks, question, top_k=3)

    provider = get_llm_provider()
    return answer_from_material(
        provider, material.session.subject, material.session.difficulty_level,
        retrieved, question,
    )
