from pydantic import BaseModel
from typing import List
import uuid as uuid_pkg
from typing import Optional

from ..models import MemberRole


# For GET Response
class ParticipantRead(BaseModel):
    id: uuid_pkg.UUID
    content: str
    role: MemberRole = MemberRole.REGULAR
    email: Optional[str] = None
    is_external: bool = False
    department_id: Optional[uuid_pkg.UUID] = None
    department: Optional[str] = None
    faculty_id: Optional[uuid_pkg.UUID] = None
    faculty: Optional[str] = None


# For PATCH Request (meeting <-> participant assignment)
class UpdateMeetingParticipants(BaseModel):
    participant_ids: List[uuid_pkg.UUID]


# Directory (admin-only) create/update
class ParticipantCreate(BaseModel):
    content: str
    role: MemberRole = MemberRole.REGULAR
    email: Optional[str] = None
    is_external: bool = False
    department_id: uuid_pkg.UUID


class ParticipantUpdate(BaseModel):
    content: Optional[str] = None
    role: Optional[MemberRole] = None
    email: Optional[str] = None
    is_external: Optional[bool] = None
    department_id: Optional[uuid_pkg.UUID] = None
