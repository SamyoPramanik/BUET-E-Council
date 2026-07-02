"""Faculty Directory Validation Data Schemas for V1 Pipelines."""

from uuid import UUID
from pydantic import BaseModel, Field


class FacultyCreateRequest(BaseModel):
    """Validation contract for registering a new institutional faculty."""
    name_bangla: str = Field(..., min_length=1, max_length=255)
    name_english: str = Field(..., min_length=1, max_length=255)


class FacultyResponse(BaseModel):
    """Complete data contract representing a single faculty record."""
    id: UUID
    name_bangla: str
    name_english: str | None

    class Config:
        from_attributes = True


class FacultyUpdateRequest(BaseModel):
    """Validation contract for partially modifying an existing faculty resource."""
    name_bangla: str | None = Field(None, min_length=1, max_length=255)
    name_english: str | None = Field(None, min_length=1, max_length=255)


class FacultyListResponse(BaseModel):
    """Envelope structure housing the full faculty directory."""
    total_records: int
    data: list[FacultyResponse]
