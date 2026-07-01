"""Agenda Management Validation Data Schemas for V1 Pipelines."""

from uuid import UUID
from pydantic import BaseModel, Field


class AgendaCreateRequest(BaseModel):
    """Validation contract for initiating a new agenda item within a meeting."""
    meeting_id: UUID = Field(..., description="The target meeting workspace UUID.")
    serial_num: int = Field(..., ge=1, description="The sequential order number of the agenda item. Must be >= 1.")


class AgendaCreateResponse(BaseModel):
    """Unified response structure indicating a successfully instantiated agenda entry."""
    id: UUID
    meeting_id: UUID
    serial_no: int
    is_supply: bool
    content: dict | None
    resolution: dict | None
    message: str

class AgendaDeletionResponse(BaseModel):
    """Structural response schema confirming individual agenda resource erasure."""
    agenda_id: UUID
    message: str

class AgendaUpdateRequest(BaseModel):
    """Validation contract for partially modifying an existing agenda item."""
    serial_num: int | None = Field(None, alias="serial_num", ge=1, description="Sequential index tracking position. Must be >= 1.")
    is_supply: bool | None = None
    content: dict | None = None
    resolution_content: dict | None = Field(None, alias="reqolusion_content", description="Maps input typo variant or clean resolution string contexts safely.")

    class Config:
        populate_by_name = True