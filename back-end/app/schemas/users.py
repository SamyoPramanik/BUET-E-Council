from typing import Optional
import uuid as uuid_pkg
from datetime import datetime

from pydantic import BaseModel

from ..models import UserRole


class UserCreate(BaseModel):
    email: str
    role: UserRole = UserRole.staff
    # If omitted, a random password is generated and emailed to the user.
    password: Optional[str] = None


class UserRead(BaseModel):
    id: uuid_pkg.UUID
    email: str
    role: UserRole
    created_at: datetime
