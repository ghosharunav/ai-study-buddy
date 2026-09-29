from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.materials import MaterialResponse, AskMaterialRequest, AskMaterialResponse
from app.services import materials_service
from app.services.session_service import SessionNotFoundError
from app.prompt_engine.chains.validated_generation import JSONGenerationError

router = APIRouter(tags=["materials"])


@router.post("/sessions/{session_id}/materials", response_model=MaterialResponse)
async def upload_material(session_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Uploads a study material file (plain text — .txt/.md work directly;
    other formats would need a dedicated parser, out of scope for this
    lightweight version) and chunks it for later retrieval.
    """
    raw_bytes = await file.read()
    try:
        raw_text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Could not read file as plain text. Please upload a .txt or .md file.",
        )

    if len(raw_text.strip()) < 20:
        raise HTTPException(status_code=400, detail="File content is too short to be useful study material.")

    try:
        material = materials_service.upload_material(db, session_id, file.filename or "untitled.txt", raw_text)
        return MaterialResponse.from_material(material)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/sessions/{session_id}/materials", response_model=list[MaterialResponse])
def list_materials(session_id: int, db: Session = Depends(get_db)):
    try:
        materials = materials_service.list_materials(db, session_id)
        return [MaterialResponse.from_material(m) for m in materials]
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/materials/{material_id}/ask", response_model=AskMaterialResponse)
def ask_material(material_id: int, payload: AskMaterialRequest, db: Session = Depends(get_db)):
    """Ask a question grounded in one uploaded material's content (RAG-lite)."""
    try:
        answer = materials_service.ask_material(db, material_id, payload.question)
        return AskMaterialResponse(**answer.model_dump())
    except materials_service.MaterialNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except JSONGenerationError as e:
        raise HTTPException(status_code=502, detail=f"AI response validation failed: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM provider error: {str(e)}")
