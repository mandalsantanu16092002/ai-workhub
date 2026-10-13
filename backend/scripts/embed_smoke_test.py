import math

from app.ai import get_ai_provider


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if not norm_a or not norm_b:
        raise ValueError("Cannot compare a zero vector")

    return dot / (norm_a * norm_b)


texts = [
    "Refunds are issued within 14 days of cancellation.",
    "The office is closed on public holidays.",
    "Our team mascot is a friendly otter.",
]

question = "How long do refunds take?"

provider = get_ai_provider()
document_vectors = provider.embed_documents(texts)
query_vector = provider.embed_query(question)

print(f"Vector length: {len(query_vector)}")

for text, vector in zip(texts, document_vectors, strict=True):
    print(f"{cosine(query_vector, vector):.3f}  {text}")