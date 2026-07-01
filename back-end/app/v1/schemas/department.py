"""Department Directory Validation Data Schemas for V1 Pipelines."""

from uuid import UUID
from pydantic import BaseModel, Field


class DepartmentCreateRequest(BaseModel):
    """Validation contract for registering a new institutional department."""
    name_bangla: str = Field(..., min_length=1, max_length=255)
    name_english: str = Field(..., min_length=1, max_length=255)
    alias: str = Field(..., min_length=1, max_length=50, description="Short code, e.g. 'CSE'.")
    faculty_id: UUID | None = Field(None, description="The parent faculty this department belongs to.")


class DepartmentResponse(BaseModel):
    """Complete data contract representing a single department record."""
    id: UUID
    name_bangla: str
    name_english: str | None
    alias: str
    faculty_id: UUID | None

    class Config:
        from_attributes = True


class DepartmentUpdateRequest(BaseModel):
    """Validation contract for partially modifying an existing department resource."""
    name_bangla: str | None = Field(None, min_length=1, max_length=255)
    name_english: str | None = Field(None, min_length=1, max_length=255)
    alias: str | None = Field(None, min_length=1, max_length=50)
    faculty_id: UUID | None = None


class DepartmentListResponse(BaseModel):
    """Envelope structure housing the full department directory."""
    total_records: int
    data: list[DepartmentResponse]
