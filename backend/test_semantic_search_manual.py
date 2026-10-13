
import uuid

from app.ai import get_ai_provider
from app.db.session import SessionLocal
from app.repositories import chunk_repo, document_repository

DOCUMENT_ID = uuid.UUID(
    "4584c247-2912-46ce-93d3-c4787697f5fd"
)

QUESTION = "Which deep learning models and technologies have I worked with?"


def main():
    provider = get_ai_provider()
    query_embedding = provider.embed_query(QUESTION)

    with SessionLocal() as db:
        document = document_repository.get(db, DOCUMENT_ID)

        if document is None:
            print("ERROR: Document not found in the configured database.")
            return

        print("Filename:", document.filename)
        print("Status:", document.status)
        print("Embedding model:", document.embedding_model)

        results = chunk_repo.search_similar(
            db,
            DOCUMENT_ID,
            query_embedding,
            top_k=5,
        )

        print(f"\nRetrieved {len(results)} chunks:\n")

        for chunk, similarity in results:
            print(
                f"Chunk {chunk.chunk_index} | "
                f"Page {chunk.page_number} | "
                f"Similarity: {similarity:.4f}"
            )
            print(chunk.content[:500])
            print("-" * 60)


if __name__ == "__main__":
    main()
