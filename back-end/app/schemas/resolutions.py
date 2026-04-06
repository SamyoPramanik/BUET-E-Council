from datetime import datetime
from typing import List, Optional
import uuid as uuid_pkg
from pydantic import BaseModel
from .agendas import AnnexureResponse, AnnexureAdd, AnnexureReorder  # reuse same shapes


# ── Resolution responses ─────────────────────────────────────────────────────

class ResolutionResponse(BaseModel):
    id:          uuid_pkg.UUID
    body:        Optional[str]   = None
    created_at:  datetime
    updated_at:  Optional[datetime] = None
    agendum_id:  uuid_pkg.UUID
    attachments: List[AnnexureResponse] = []


# ── Create / Update ──────────────────────────────────────────────────────────

class ResolutionCreate(BaseModel):
    """
    POST /resolutions/
    Creates a blank resolution tied to an existing agendum.
    Body is filled in later via PATCH.
    """
    agendum_id: uuid_pkg.UUID


class ResolutionUpdate(BaseModel):
    """PATCH /resolutions/{resolution_id}"""
    body: Optional[str] = None


# ── File attachment (reuse agendas shapes, renamed for clarity) ──────────────

ResolutionAttachmentAdd     = AnnexureAdd
ResolutionAttachmentReorder = AnnexureReorder


class ResolutionAttachmentResponse(AnnexureResponse):
    """Identical shape to AnnexureResponse — subclassed for semantic clarity."""
    pass


# ── PDF ──────────────────────────────────────────────────────────────────────

class ResolutionPDFResponse(BaseModel):
    resolution_id: uuid_pkg.UUID
    pdf_path:      Optional[str] = None   # None when cleared