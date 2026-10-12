
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentCreate


class DocumentService:
    """Business logic for document operations."""

    def __init__(self) -> None:
        self.repository = DocumentRepository()

    def create_document(
        self,
        db: Session,
        payload: DocumentCreate,
    ) -> Document:
        document = Document(
            filename=payload.filename.strip(),
            content_type=payload.content_type.strip(),
            file_size=payload.file_size,
            stored_path=payload.stored_path.strip(),
        )

        if not document.filename:
            raise AppError(
                422,
                "invalid_filename",
                "Filename cannot be empty.",
            )

        if not document.content_type:
            raise AppError(
                422,
                "invalid_content_type",
                "Content type cannot be empty.",
            )

        if not document.stored_path:
            raise AppError(
                422,
                "invalid_stored_path",
                "Stored path cannot be empty.",
            )

        try:
            return self.repository.create(db, document)
        except Exception:
            db.rollback()
            raise

    def get_document(
        self,
        db: Session,
        document_id: UUID,
    ) -> Document:
        document = self.repository.get_by_id(db, document_id)

        if document is None:
            raise AppError(
                404,
                "document_not_found",
                "The requested document was not found.",
            )

        return document

    def list_documents(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Document], int]:
        return self.repository.list_documents(
            db,
            skip=skip,
            limit=limit,
        )

    def delete_document(
        self,
        db: Session,
        document_id: UUID,
    ) -> None:
        document = self.get_document(db, document_id)

        try:
            self.repository.delete(db, document)
        except Exception:
            db.rollback()
            raise
