from datetime import datetime
from typing import Any, List, Optional
import uuid as uuid_pkg
from pydantic import BaseModel


class MeetingSummary(BaseModel):
    id:           Any
    serial_num:   int
    title_plain:  str
    meeting_date: Optional[datetime]
    is_finished:  bool


class PaginatedMeetingResponse(BaseModel):
    total_count: int
    page:        int
    limit:       int
    data:        List[MeetingSummary]


class MeetingUpdate(BaseModel):
    serial_num:        Optional[int]           = None
    is_academic:       Optional[bool]          = None
    title:             Optional[str]           = None
    description:       Optional[str]           = None
    conclusion:        Optional[str]           = None
    is_finished:       Optional[bool]          = None
    meeting_date:      Optional[datetime]      = None
    president_card_id: Optional[uuid_pkg.UUID] = None


class MeetingPDFResponse(BaseModel):
    """Returned after generating or clearing a meeting-level PDF."""
    meeting_id:     uuid_pkg.UUID
    agenda_pdf:     Optional[str] = None   # relative path; None when cleared
    resolution_pdf: Optional[str] = None