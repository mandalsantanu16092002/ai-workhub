from io import BytesIO
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from pypdf import PdfWriter

from app.db.session import SessionLocal
from app.main import app
from app.models.document import DocumentChunk

client = TestClient(app)


def make_test_pdf() -> bytes:
    """Generate a minimal valid PDF for upload tests."""
    buffer = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.write(buffer)
    return buffer.getvalue()


def upload_test_document() -> dict:
    """Upload a PDF using the current multipart API."""
    response = client.post(
        "/api/documents",
        files={
            "file": (
                "test-document.pdf",
                make_test_pdf(),
                "application/pdf",
            )
        },
    )
    assert response.status_code == 202, response.text
    return response.json()


def test_create_document():
    document = upload_test_document()

    try:
        assert document["filename"] == "test-document.pdf"
        assert document["content_type"] == "application/pdf"
        assert document["file_size"] > 0
        assert document["id"]
        assert "stored_path" not in document
        assert document["status"] in {
            "processing", "ready", "failed"
        }
    finally:
        client.delete(f"/api/documents/{document['id']}")



def test_list_documents():
    document = upload_test_document()

    try:
        response = client.get("/api/documents")
        assert response.status_code == 200

        data = response.json()

        # The API returns a list directly.
        assert isinstance(data, list)

        document_ids = [item["id"] for item in data]
        assert document["id"] in document_ids
    finally:
        client.delete(f"/api/documents/{document['id']}")


def test_get_document():
    document = upload_test_document()

    try:
        response = client.get(
            f"/api/documents/{document['id']}"
        )
        assert response.status_code == 200
        assert response.json()["id"] == document["id"]
    finally:
        client.delete(f"/api/documents/{document['id']}")


def test_delete_document():
    document = upload_test_document()

    response = client.delete(
        f"/api/documents/{document['id']}"
    )
    assert response.status_code == 204
    assert response.content == b""

    response = client.get(
        f"/api/documents/{document['id']}"
    )
    assert response.status_code == 404


def test_upload_requires_file():
    response = client.post(
        "/api/documents",
        json={
            "filename": "",
            "content_type": "application/pdf",
            "file_size": 0,
        },
    )

    assert response.status_code == 422

    data = response.json()
    assert data["error"] == "validation_error"
    assert any(
        detail["field"] == "file"
        for detail in data["details"]
    )


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
    document = upload_test_document()
    document_id = UUID(document["id"])

    try:
        with SessionLocal() as db:
            chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=0,
                content="This is a test document chunk.",
                page_number=1,
            )
            db.add(chunk)
            db.commit()

        response = client.delete(
            f"/api/documents/{document['id']}"
        )
        assert response.status_code == 204

        with SessionLocal() as db:
            remaining_chunks = db.scalar(
                select(func.count())
                .select_from(DocumentChunk)
                .where(
                    DocumentChunk.document_id == document_id
                )
            )
            assert remaining_chunks == 0
    finally:
        client.delete(f"/api/documents/{document['id']}")


def test_invalid_pdf_content_is_rejected():
    response = client.post(
        "/api/documents",
        files={
            "file": (
                "invalid.pdf",
                b"This is not a PDF file.",
                "application/pdf",
            )
        },
    )

    assert response.status_code in {400, 415, 422}
