import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.document import DocumentChunk


def replace_chunks(
    db: Session,
    document_id: uuid.UUID,
    chunks: list[DocumentChunk],
) -> None:
    db.execute(
        delete(DocumentChunk).where(
            DocumentChunk.document_id == document_id
        )
    )
    db.add_all(chunks)


def search_similar(
    db: Session,
    document_id: uuid.UUID,
    query_embedding: list[float],
    *,
    top_k: int,
) -> list[tuple[DocumentChunk, float]]:
    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    ).label("distance")

    statement = (
        select(DocumentChunk, distance)
        .where(
            DocumentChunk.document_id == document_id,
            DocumentChunk.embedding.is_not(None),
        )
        .order_by(distance)
        .limit(top_k)
    )

    return [
        (chunk, 1.0 - float(distance_value))
        for chunk, distance_value in db.execute(statement).all()
    ]