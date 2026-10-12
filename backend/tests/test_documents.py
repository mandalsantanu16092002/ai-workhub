from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.main import app
from app.models.document import DocumentChunk

client = TestClient(app)
def create_test_document() -> dict:
    """Create a uniquely named test document."""
    unique_id = uuid4().hex

    response = client.post(
        "/api/documents",
        json={
            "filename": f"test-{unique_id}.pdf",
            "content_type": "application/pdf",
            "file_size": 1024,
            "stored_path": f"uploads/test-{unique_id}.pdf",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()
def test_create_document():
    document = create_test_document()
    try:
        assert document["filename"].endswith(".pdf")
        assert document["status"] == "uploaded"
        assert document["file_size"] == 1024
        assert "id" in document
        assert "stored_path" not in document
    finally:
        client.delete(f"/api/documents/{document['id']}")
def test_list_documents():
    document = create_test_document()
    try:
        response = client.get("/api/documents")
        assert response.status_code == 200
        data = response.json()
        document_ids = [item["id"] for item in data["items"]]
        assert document["id"] in document_ids
        assert data["total"] >= 1
    finally:
        client.delete(f"/api/documents/{document['id']}")

def test_get_document():
    document = create_test_document()

    try:
        response = client.get(
            f"/api/documents/{document['id']}"
        )
        assert response.status_code == 200
        assert response.json()["id"] == document["id"]
    finally:
        client.delete(f"/api/documents/{document['id']}")

def test_delete_document():
    document = create_test_document()

    response = client.delete(
        f"/api/documents/{document['id']}"
    )
    assert response.status_code == 204
    assert response.content == b""
    get_response = client.get(
        f"/api/documents/{document['id']}"
    )
    assert get_response.status_code == 404

def test_invalid_document_payload():
    response = client.post(
        "/api/documents",
        json={
            "filename": "",
            "content_type": "application/pdf",
            "file_size": 0,
            "stored_path": "uploads/invalid.pdf",
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "validation_error"
    invalid_fields = {
        detail["field"] for detail in data["details"]
    }
    assert "filename" in invalid_fields
    assert "file_size" in invalid_fields

def test_get_missing_document():
    missing_id = "00000000-0000-0000-0000-000000000001"

    response = client.get(
        f"/api/documents/{missing_id}"
    )
    assert response.status_code == 404
    assert response.json()["error"] == "document_not_found"

def test_invalid_document_uuid():
    response = client.get(
        "/api/documents/not-a-valid-uuid"
    )
    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"

def test_delete_document_cascades_to_chunks():
    document = create_test_document()
    document_id = UUID(document["id"])
    # Add a chunk associated with this document.
    with SessionLocal() as db:
        chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=0,
            content="This is a test document chunk.",
        )
        db.add(chunk)
        db.commit()
    # Delete the parent document through the API.
    response = client.delete(
        f"/api/documents/{document['id']}"
    )
    assert response.status_code == 204
   # Confirm PostgreSQL removed the associated chunk.
    with SessionLocal() as db:
        remaining_chunks = db.scalar(
            select(func.count())
            .select_from(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
        )
 assert remaining_chunks == 0