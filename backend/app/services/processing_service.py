import logging
import uuid
from pathlib import Path

from app.ai import get_ai_provider
from app.ai.base import AIProviderError
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.document import DocumentChunk, DocumentStatus
from app.repositories import chunk_repo, document_repository
from app.services.chunking import chunk_pages
from app.services.pdf_extraction import ExtractionError, extract_pages

logger = logging.getLogger(__name__)


def process_document(document_id: uuid.UUID) -> None:
    settings = get_settings()

    with SessionLocal() as db:
        document = document_repository.get(db, document_id)

        if document is None or not document.stored_path:
            logger.warning(
                "Document %s vanished before processing",
                document_id,
            )
            return

        try:
            result = extract_pages(
                Path(document.stored_path),
                max_pages=settings.max_pages,
            )

            chunks = chunk_pages(
                result.pages,
                size=settings.chunk_size,
                overlap=settings.chunk_overlap,
            )

            if not chunks:
                raise ExtractionError(
                    "No usable text could be extracted from this PDF."
                )

            vectors = get_ai_provider().embed_documents(
                [chunk.text for chunk in chunks]
            )

            if len(vectors) != len(chunks):
                raise AIProviderError(
                    "The AI service returned an unexpected number of embeddings."
                )

            rows = [
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    page_number=chunk.page_number,
                    content=chunk.text,
                    embedding=vector,
                )
                for index, (chunk, vector) in enumerate(
                    zip(chunks, vectors, strict=True)
                )
            ]

            chunk_repo.replace_chunks(db, document.id, rows)

            document_repository.update_processing_result(
                db,
                document,
                status=DocumentStatus.READY,
                page_count=result.page_count,
                error_message=None,
                embedding_model=settings.embedding_signature,
            )

        except (ExtractionError, AIProviderError) as exc:
            db.rollback()
            document_repository.update_processing_result(
                db,
                document,
                status=DocumentStatus.FAILED,
                error_message=str(exc),
            )

        except Exception:
            logger.exception(
                "Unexpected failure processing document %s",
                document_id,
            )
            db.rollback()
            document_repository.update_processing_result(
                db,
                document,
                status=DocumentStatus.FAILED,
                error_message=(
                    "Something went wrong while processing the document."
                ),
            )