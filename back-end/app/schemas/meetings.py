from pydantic import BaseModel, field_validator
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

class MeetingSummary(BaseModel):
    id: Any # Including ID is usually helpful for frontend keys
    serial_num: int
    title_plain: str
    meeting_date: Optional[datetime]
    is_finished: bool

class PaginatedMeetingResponse(BaseModel):
    total_count: int
    page: int
    limit: int
    data: List[MeetingSummary]

# Schema for partial updates
class MeetingUpdate(BaseModel):
    serial_num: Optional[int] = None
    is_academic: Optional[bool] = None
    title: Optional[Dict[str, Any]] = None
    description: Optional[Dict[str, Any]] = None
    conclusion: Optional[Dict[str, Any]] = None
    is_finished: Optional[bool] = None
    meeting_date: Optional[datetime] = None

    @field_validator("meeting_date") # New V2 syntax
    @classmethod # V2 field_validators must be class methods
    def date_must_not_be_past(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v and v < datetime.now(timezone.utc):
            raise ValueError("Meeting date cannot be in the past")
        return v