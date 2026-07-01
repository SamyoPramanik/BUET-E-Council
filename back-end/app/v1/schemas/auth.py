"""Authentication Validation Data Schemas for V1 Pipelines."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr
from app.models import UserRole


class LoginRequest(BaseModel):
    """Validation contract for incoming login credential verification blocks."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Unified structural response sent to the client upon successful session creation."""
    session_id: UUID
    role: UserRole
    expires_at: datetime
    message: str

class LogoutResponse(BaseModel):
    """Structural response schema confirming successful session termination."""
    message: str
    terminated_session_id: UUID

class SessionRevocationResponse(BaseModel):
    """Structural response schema confirming successful targeted session destruction."""
    message: str
    revoked_session_id: UUID

class BulkSessionRevocationResponse(BaseModel):
    """Structural response schema confirming bulk session termination actions."""
    message: str
    revoked_sessions_count: int

