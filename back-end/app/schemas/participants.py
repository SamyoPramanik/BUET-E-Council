from pydantic import BaseModel
from typing import List
import uuid as uuid_pkg
from typing import Optional

# For GET Response
class ParticipantRead(BaseModel):
    id: uuid_pkg.UUID
    content: str
    email: Optional[str] = None
    department_id: Optional[uuid_pkg.UUID] = None
    department: Optional[str] = None
    faculty_id: Optional[uuid_pkg.UUID] = None
    faculty: Optional[str] = None

# For PATCH Request
class UpdateMeetingParticipants(BaseModel):
    participant_ids: List[uuid_pkg.UUID]