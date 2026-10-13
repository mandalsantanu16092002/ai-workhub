import re
import uuid
from pathlib import Path
from typing import BinaryIO

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import AppError
from app.models.document import Document, DocumentStatus
from app.repositories import document_repository

_COPY_CHUNK_BYTES = 1024 * 1024
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")


def _storage_dir() -> Path:
    directory = Path(get_settings().storage_dir).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _clean_filename(raw: str | None) -> str:
    name = Path((raw or "").replace("\\", "/")).name
    name = _CONTROL_CHARS.sub("", name).strip()
    return name[-255:]


def _write_limited(
    source: BinaryIO,
    destination: Path,
    max_bytes: int,
) -> int:
    total = 0

    with destination.open("wb") as output:
        while chunk := source.read(_COPY_CHUNK_BYTES):
            total += len(chunk)

            if total > max_bytes:
                raise AppError(
                    413,
                    "file_too_large",
                    f"The file is too large. The maximum is "
                    f"{max_bytes // (1024 * 1024)} MB.",
                )

            output.write(chunk)

    return total


def _looks_like_pdf(path: Path) -> bool:
    with path.open("rb") as file:
        return b"%PDF-" in file.read(1024)


def save_upload(db: Session, upload: UploadFile) -> Document:
    settings = get_settings()

    filename = _clean_filename(upload.filename)

    if not filename.lower().endswith(".pdf"):
        raise AppError(
            400,
            "invalid_file_type",
            "Only PDF files are supported.",
        )

    document_id = uuid.uuid4()
    destination = _storage_dir() / f"{document_id}.pdf"

    try:
        size = _write_limited(
            upload.file,
            destination,
            settings.max_upload_mb * 1024 * 1024,
        )

        if size == 0:
            raise AppError(
                400,
                "empty_file",
                "The uploaded file is empty.",
            )

        if not _looks_like_pdf(destination):
            raise AppError(
                400,
                "invalid_pdf",
                "The file is not a valid PDF.",
            )

        return document_repository.create(
            db,
            document_id=document_id,
            filename=filename,
            content_type="application/pdf",
            file_size=size,
            stored_path=str(destination),
            status=DocumentStatus.PROCESSING,
        )

    except Exception:
        destination.unlink(missing_ok=True)
        raise


def get_document_or_404(
    db: Session,
    document_id: uuid.UUID,
) -> Document:
    document = document_repository.get_by_id(db, document_id)

    if document is None:
        raise AppError(
            404,
            "document_not_found",
            "Document not found.",
        )

    return document


def list_documents(
    db: Session,
    *,
    limit: int,
    offset: int,
) -> list[Document]:
    return document_repository.list_documents(
        db,
        limit=limit,
        offset=offset,
    )


def delete_document(db: Session, document_id: uuid.UUID) -> None:
    document = get_document_or_404(db, document_id)
    stored_path = document.stored_path

    document_repository.delete(db, document)

    if stored_path:
        Path(stored_path).unlink(missing_ok=True)