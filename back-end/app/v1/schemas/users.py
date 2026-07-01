"""User Management Validation Data Schemas for V1 Pipelines."""

from pydantic import BaseModel, EmailStr
from uuid import UUID
from app.models import UserRole
from datetime import datetime


class UserRegisterRequest(BaseModel):
    """Validation contract checking inbound user batch insertion records."""
    email: EmailStr
    role: UserRole


class UserRegisterResult(BaseModel):
    """Metadata response showing an individual processed record summary block."""
    id: UUID
    email: EmailStr
    role: UserRole
    status: str


class UserRegisterResponseList(BaseModel):
    """Master response schema returned to the administrator upon successful batch execution."""
    processed_records: list[UserRegisterResult]

class SessionHistoryRecord(BaseModel):
    """Structural layout tracking a single recorded database session block."""
    session_id: UUID
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime
    expires_at: datetime
    is_active: bool  # Computed field showing if the session is currently valid

    class Config:
        from_attributes = True