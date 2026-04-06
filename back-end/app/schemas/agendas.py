from datetime import datetime
from typing import List, Optional
import uuid as uuid_pkg
from pydantic import BaseModel, field_validator


# ── File attachment (shared shape) ───────────────────────────────────────────

class AnnexureResponse(BaseModel):
    id:            uuid_pkg.UUID
    file_id:       uuid_pkg.UUID
    order:         int
    original_filename: str
    mime_type:     str
    size_bytes:    int
    path:          str           # relative — frontend prepends MEDIA_ROOT url


# ── Resolution (inline inside AgendumResponse) ───────────────────────────────

class InlineResolutionResponse(BaseModel):
    id:         uuid_pkg.UUID
    body:       Optional[str]   = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    attachments: List[AnnexureResponse] = []


# ── Agendum responses ────────────────────────────────────────────────────────

class AgendumResponse(BaseModel):
    id:               uuid_pkg.UUID
    serial:           int
    body:             Optional[str]   = None
    is_supplementary: bool
    created_at:       datetime
    updated_at:       Optional[datetime] = None
    meeting_id:       uuid_pkg.UUID
    annexures:        List[AnnexureResponse]          = []
    resolution:       Optional[InlineResolutionResponse] = None


# ── Create / Update ──────────────────────────────────────────────────────────

class AgendumCreate(BaseModel):
    """
    POST /agendas/
    Creates a blank agenda item under a meeting.
    `body` is intentionally omitted — the editor fills it in later.
    """
    meeting_id:       uuid_pkg.UUID
    serial:           int
    is_supplementary: bool = False


class AgendumUpdate(BaseModel):
    """
    PATCH /agendas/{agendum_id}
    At least one field must be provided (enforced in the router).
    """
    body:             Optional[str]  = None
    serial:           Optional[int]  = None
    is_supplementary: Optional[bool] = None

    @field_validator("body", "serial", "is_supplementary", mode="before")
    @classmethod
    def at_least_one(cls, v):
        return v  # actual check is done in the router after model_dump(exclude_unset=True)


# ── File attachment ──────────────────────────────────────────────────────────

class AnnexureAdd(BaseModel):
    """POST /agendas/{agendum_id}/files"""
    file_id: uuid_pkg.UUID
    order:   int = 1


class AnnexureReorder(BaseModel):
    """PATCH /agendas/{agendum_id}/files/{annexure_id}"""
    order: int


# ── PDF ──────────────────────────────────────────────────────────────────────

class AgendumPDFResponse(BaseModel):
    agendum_id: uuid_pkg.UUID
    pdf_path:   Optional[str] = None   # None when cleared