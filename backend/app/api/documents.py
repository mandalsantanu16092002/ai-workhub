import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.document import DocumentRead
from app.services import document_service, processing_service
from app.ai import get_ai_provider
from app.ai.base import AIProvider
from app.schemas.qa import AskRequest, AskResponse
from app.services import qa_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "",
    response_model=DocumentRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    document = document_service.save_upload(db, file)

    background_tasks.add_task(
        processing_service.process_document,
        document.id,
    )

    return document


@router.get("", response_model=list[DocumentRead])
def list_documents(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return document_service.list_documents(
        db,
        limit=limit,
        offset=offset,
    )


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    return document_service.get_document_or_404(db, document_id)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    document_service.delete_document(db, document_id)

@router.post("/{document_id}/ask", response_model=AskResponse)
def ask_document(
    document_id: uuid.UUID,
    payload: AskRequest,
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_ai_provider),
):
    return qa_service.ask_question(
        db,
        document_id,
        payload.question,
        provider,
    )