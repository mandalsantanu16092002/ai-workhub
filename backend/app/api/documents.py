from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.document import (
    DocumentCreate,
    DocumentList,
    DocumentRead,
)
from app.services.document_service import DocumentService


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

document_service = DocumentService()


@router.post(
    "",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    payload: DocumentCreate,
    db: Session = Depends(get_db),
) -> DocumentRead:
    return document_service.create_document(db, payload)


@router.get(
    "",
    response_model=DocumentList,
)
def list_documents(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> DocumentList:
    documents, total = document_service.list_documents(
        db,
        skip=skip,
        limit=limit,
    )

    return DocumentList(
        items=documents,
        total=total,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentRead,
)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
) -> DocumentRead:
    return document_service.get_document(db, document_id)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
) -> Response:
    document_service.delete_document(db, document_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
