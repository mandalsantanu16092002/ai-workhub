from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk


class DocumentRepository:
    """Database operations for documents and their chunks."""

    def create(
        self,
        db: Session,
        document: Document,
    ) -> Document:
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    def get_by_id(
        self,
        db: Session,
        document_id: UUID,
    ) -> Document | None:
        statement = select(Document).where(
            Document.id == document_id
        )
        return db.scalar(statement)

    def list_documents(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Document], int]:
        statement = (
            select(Document)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        documents = list(db.scalars(statement).all())

        count_statement = select(func.count()).select_from(Document)
        total = db.scalar(count_statement) or 0

        return documents, total

    def delete(
        self,
        db: Session,
        document: Document,
    ) -> None:
        db.delete(document)
        db.commit()

    def add_chunks(
        self,
        db: Session,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]:
        db.add_all(chunks)
        db.commit()

        for chunk in chunks:
            db.refresh(chunk)

        return chunks