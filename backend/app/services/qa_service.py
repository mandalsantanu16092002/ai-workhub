
import logging
import uuid

from sqlalchemy.orm import Session

from app.ai import get_ai_provider
from app.ai.base import AIProviderError
from app.core.config import get_settings
from app.core.errors import AppError
from app.models.document import DocumentStatus
from app.repositories import chunk_repo, document_repository
from app.schemas.qa import AnswerSource, AskResponse, GeneratedAnswer
from app.services.qa_prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)

NOT_FOUND_MESSAGE = (
    "I couldn't find sufficiently relevant information "
    "in this document to answer that question."
)


def ask_document(
    db: Session,
    document_id: uuid.UUID,
    question: str,
) -> AskResponse:
    settings = get_settings()
    document = document_repository.get(db, document_id)

    if document is None:
        raise AppError(404, "document_not_found", "Document not found.")

    status = getattr(document.status, "value", document.status)
    if status != DocumentStatus.READY.value:
        raise AppError(
            409,
            "document_not_ready",
            "This document is not ready yet. Wait until its status is 'ready'.",
        )

    if document.embedding_model != settings.embedding_signature:
        raise AppError(
            409,
            "reindex_required",
            "This document was indexed with a different embedding model. "
            "Upload it again to re-index it.",
        )

    provider = get_ai_provider()

    try:
        query_embedding = provider.embed_query(question)
    except AIProviderError as exc:
        logger.warning("Query embedding failed for document %s", document_id)
        raise AppError(
            502,
            "ai_unavailable",
            "The AI service is temporarily unavailable. Please try again.",
        ) from exc

    matches = chunk_repo.search_similar(
        db,
        document.id,
        query_embedding,
        top_k=settings.retrieval_top_k,
    )

    # Keep only chunks that meet the configured relevance threshold.
    matches = [
        (chunk, score)
        for chunk, score in matches
        if score >= settings.min_similarity
    ]

    logger.info(
        "Retrieved %s relevant chunks for document %s",
        len(matches),
        document_id,
    )

    if not matches:
        return AskResponse(answer=NOT_FOUND_MESSAGE, sources=[])

    contexts = [
        {
            "chunk_index": chunk.chunk_index,
            "page_number": chunk.page_number,
            "content": chunk.content,
        }
        for chunk, _score in matches
    ]

    try:
        generated = provider.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=build_user_prompt(question, contexts),
            schema=GeneratedAnswer,
        )
    except AIProviderError as exc:
        logger.warning("Answer generation failed for document %s", document_id)
        raise AppError(
            502,
            "ai_unavailable",
            "The AI service is temporarily unavailable. Please try again.",
        ) from exc

    if not generated.answer.strip():
        return AskResponse(answer=NOT_FOUND_MESSAGE, sources=[])

    # Construct citations from retrieved database rows, not model-generated IDs.
    sources = [
        AnswerSource(
            chunk_index=chunk.chunk_index,
            page_number=chunk.page_number,
            excerpt=chunk.content[:300],
            similarity=round(float(score), 4),
        )
        for chunk, score in matches
    ]

    return AskResponse(
        answer=generated.answer.strip(),
        sources=sources,
    )
