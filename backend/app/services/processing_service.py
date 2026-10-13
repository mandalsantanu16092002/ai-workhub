import logging
import uuid
from pathlib import Path

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.document import DocumentChunk, DocumentStatus
from app.repositories import chunk_repo, document_repository
from app.services.pdf_extraction import ExtractionError, extract_pages

logger = logging.getLogger(__name__)


def _mark_failed(
    db,
    document_id: uuid.UUID,
    message: str,
) -> None:
    db.rollback()

    document = document_repository.get_by_id(db, document_id)

    if document is None:
        return

    document.status = DocumentStatus.FAILED
    document.error_message = message
    db.commit()


def process_document(document_id: uuid.UUID) -> None:
    """Process a stored PDF using a fresh database session."""
    with SessionLocal() as db:
        document = document_repository.get_by_id(db, document_id)

        if document is None or not document.stored_path:
            logger.warning(
                "Document %s disappeared before processing",
                document_id,
            )
            return

        try:
            result = extract_pages(
                Path(document.stored_path),
                max_pages=get_settings().max_pages,
            )

            chunks = [
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    page_number=page.page_number,
                    content=page.text,
                )
                for index, page in enumerate(result.pages)
            ]

            chunk_repo.replace_chunks(db, document.id, chunks)

            document.page_count = result.page_count
            document.error_message = None
            document.status = DocumentStatus.READY

            # Chunks and document status commit atomically.
            db.commit()

        except ExtractionError as exc:
            _mark_failed(db, document_id, str(exc))

        except Exception:
            logger.exception(
                "Unexpected failure processing document %s",
                document_id,
            )
            _mark_failed(
                db,
                document_id,
                "Something went wrong while processing the document.",
            )
