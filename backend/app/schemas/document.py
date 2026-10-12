
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.document import DocumentStatus


class DocumentCreate(BaseModel):
    """Fields required to create a document record."""

    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=100)
    file_size: int = Field(gt=0)
    stored_path: str = Field(min_length=1, max_length=500)


class DocumentRead(BaseModel):
    """Public document representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    content_type: str
    file_size: int
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime


class DocumentList(BaseModel):
    """Response containing a list of documents."""

    items: list[DocumentRead]
    total: int


class DocumentChunkRead(BaseModel):
    """Public representation of a document text chunk."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    created_at: datetime
