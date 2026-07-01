"""Meeting Management Validation Data Schemas for V1 Pipelines."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.models import MeetingStatus


class MeetingCreateRequest(BaseModel):
    """Validation contract for initiating a new council meeting profile."""
    is_academic: bool
    meeting_date: datetime
    serial_num: int = Field(..., ge=1, description="The sequence ledger index. Must be greater than or equal to 1.")


class MeetingCreateResponse(BaseModel):
    """Unified response structure indicating successful meeting resource instantiation."""
    id: UUID
    title: str
    serial_num: int
    is_academic: bool
    status: MeetingStatus
    meeting_date: datetime
    message: str

class MeetingSummaryRecord(BaseModel):
    """Clean data contract representing a subset of meeting attributes for tabular layouts."""
    id: UUID
    title: str
    meeting_date: datetime
    status: MeetingStatus

class PaginatedMeetingListResponse(BaseModel):
    """Envelope structure housing subset query payloads alongside layout navigation offsets."""
    total_records: int
    limit: int
    offset: int
    data: list[MeetingSummaryRecord]

class MeetingDetailsResponse(BaseModel):
    """Complete data contract representing all database attributes for a specific meeting instance."""
    id: UUID
    title: str
    description: str | None
    conclusion: str | None
    president: str | None
    serial_num: int
    status: MeetingStatus
    is_academic: bool
    created_at: datetime
    agenda_file_id: UUID | None
    resolution_file_id: UUID | None
    meeting_date: datetime

    class Config:
        from_attributes = True

class MeetingUpdateRequest(BaseModel):
    """Validation contract for partially modifying an existing meeting resource."""
    serial_num: int | None = Field(None, ge=1, description="Must be greater than or equal to 1 if provided.")
    is_academic: bool | None = None
    meeting_date: datetime | None = Field(None, alias="date") # Maps the incoming json 'date' key safely
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    president: str | None = Field(None, max_length=255)
    conclusion: str | None = None
    status: MeetingStatus | None = None

    agenda_file_id: UUID | None = Field(None, description="The UUID of the uploaded agenda file asset. Set to null to remove.")
    resolution_file_id: UUID | None = Field(None, description="The UUID of the uploaded resolution file asset. Set to null to remove.")

    class Config:
        populate_by_name = True # Allows processing raw or aliased names smoothly

class MeetingMembersSyncRequest(BaseModel):
    """Validation contract for syncing the complete member roster of a meeting."""
    member_ids: list[UUID] = Field(..., description="Array of member UUIDs to assign to this meeting. Can be empty.")

class MeetingMembersSyncResponse(BaseModel):
    """Structural response confirming the changes made during the roster sync."""
    meeting_id: UUID
    members_added_count: int
    members_removed_count: int
    total_active_members: int
    message: str

class MeetingSignaturesSyncRequest(BaseModel):
    """Validation contract for syncing the complete signature list of a meeting."""
    signature_ids: list[UUID] = Field(..., description="Array of signature UUIDs to assign to this meeting. Can be empty.")

class MeetingSignaturesSyncResponse(BaseModel):
    """Structural response confirming the modifications made during the signatures sync."""
    meeting_id: UUID
    signatures_added_count: int
    signatures_removed_count: int
    total_active_signatures: int
    message: str

class AgendaMinimalRecord(BaseModel):
    """Clean representation of an agenda item row for list views."""
    id: UUID
    serial_no: int
    content: dict | None
    resolution: dict | None

class GroupedAgendaResponse(BaseModel):
    """Response wrapper splitting agenda items into regular and supplementary blocks."""
    regular_agenda: list[AgendaMinimalRecord]
    supplementary_agenda: list[AgendaMinimalRecord]

class BulkAgendaDeletionResponse(BaseModel):
    """Structural response schema confirming bulk agenda data erasure."""
    meeting_id: UUID
    is_supply: bool
    deleted_agenda_count: int
    message: str