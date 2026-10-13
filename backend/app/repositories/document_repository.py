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


def list_documents(
    db: Session,
    *,
    limit: int,
    offset: int,
) -> list[Document]:
    stmt = (
        select(Document)
        .order_by(Document.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt))


def delete(db: Session, document: Document) -> None:
    db.delete(document)
    db.commit()
