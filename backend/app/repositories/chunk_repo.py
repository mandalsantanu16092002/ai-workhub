import uuid

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.document import DocumentChunk


def replace_chunks(
    db: Session,
    document_id: uuid.UUID,
    chunks: list[DocumentChunk],
) -> None:
    """Replace all chunks for a document without committing."""
    db.execute(
        delete(DocumentChunk).where(
            DocumentChunk.document_id == document_id
        )
    )
    db.add_all(chunks)