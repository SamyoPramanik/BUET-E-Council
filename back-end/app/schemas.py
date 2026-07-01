from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from app.models import UserRole

class UserSecurePayload(BaseModel):
    """The unified internal user context injected into secured routes."""
    id: UUID
    email: EmailStr
    role: UserRole
    created_at: datetime
    
    # Session metadata attributes
    session_id: UUID
    session_expires_at: datetime
    ip_address: str | None = None
    user_agent: str | None = None

    class Config:
        from_attributes = True