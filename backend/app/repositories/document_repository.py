
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentStatus



def create(
    db: Session,
    *,
    document_id: uuid.UUID,
    filename: str,
    content_type: str,
    file_size: int,
    stored_path: str,
    status: DocumentStatus,
) -> Document:
    document = Document(
        id=document_id,
        filename=filename,
        content_type=content_type,
        file_size=file_size,
        stored_path=stored_path,
        status=status,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document



def get_by_id(
    db: Session,
    document_id: uuid.UUID,
) -> Document | None:
    return db.get(Document, document_id)

def get(
    db: Session,
    document_id: uuid.UUID,
) -> Document | None:
    return get_by_id(db, document_id)



def list_documents(
    db: Session,
    *,
    limit: int = 50,
    offset: int = 0,
) -> list[Document]:
    statement = (
        select(Document)
        .order_by(Document.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(statement).all())



def delete(db: Session, document: Document) -> None:
    db.delete(document)
    db.commit()


def update_processing_result(
    db: Session,
    document: Document,
    *,
    status: DocumentStatus,
    page_count: int | None = None,
    error_message: str | None = None,
    embedding_model: str | None = None,
) -> None:
    document.status = status.value

    if page_count is not None:
        document.page_count = page_count

    if embedding_model is not None:
        document.embedding_model = embedding_model

    document.error_message = error_message
    db.commit()
