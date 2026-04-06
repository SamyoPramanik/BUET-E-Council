"""
schemas/signature_cards.py
===========================
Pydantic / SQLModel response + request schemas for SignatureCard endpoints.
"""

from __future__ import annotations

import uuid as uuid_pkg
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ── Request schemas ───────────────────────────────────────────────────────────

class SignatureCardCreate(BaseModel):
    """Body for POST /signature-cards/"""
    content: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Multi-line label displayed below the signature line.",
        examples=["(অধ্যাপক ডঃ সত্য প্রসাদ মজুমদার)\nউপাচার্য\nও\nএকাডেমিক কাউন্সিলের সভাপতি"],
    )


class SignatureCardUpdate(BaseModel):
    """Body for PATCH /signature-cards/{id}  — all fields optional."""
    content: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=1000,
    )


class MeetingSignatureAdd(BaseModel):
    """Body for POST /meetings/{id}/signature-cards"""
    signature_card_id: uuid_pkg.UUID
    order: int = Field(default=1, ge=1)


class MeetingSignatureReorder(BaseModel):
    """Body for PATCH /meetings/{id}/signature-cards/{sig_id}"""
    order: int = Field(..., ge=1)


# ── Response schemas ──────────────────────────────────────────────────────────

class SignatureCardResponse(BaseModel):
    id:         uuid_pkg.UUID
    content:    str
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedSignatureCardResponse(BaseModel):
    total_count: int
    page:        int
    limit:       int
    data:        List[SignatureCardResponse]