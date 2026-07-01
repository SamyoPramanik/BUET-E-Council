"""File Registry Management Validation Data Schemas for V1 Pipelines."""

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    """Unified response structure confirming successful file ingestion and indexing."""
    id: UUID
    original_filename: str
    mime_type: str
    file_size_bytes: int
    created_at: datetime
    message: str