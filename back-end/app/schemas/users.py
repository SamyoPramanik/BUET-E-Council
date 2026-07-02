from typing import Optional
import uuid as uuid_pkg
from datetime import datetime

from pydantic import BaseModel

from ..models import UserRole


class UserCreate(BaseModel):
    email: str
    # New accounts default to viewer (read-only). Admins can promote a user
    # to staff/admin later via PATCH /users/{id}/role.
    role: UserRole = UserRole.viewer
    # If omitted, a random password is generated and emailed to the user.
    password: Optional[str] = None


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserRead(BaseModel):
    id: uuid_pkg.UUID
    email: str
    role: UserRole
    created_at: datetime
