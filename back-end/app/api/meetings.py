from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select, func, desc
from app.database import engine, get_session
from app.models import Meeting, User, UserRole
from app.dependencies import get_current_user
from datetime import datetime
import uuid as uuid_pkg
from ..schemas.meetings import MeetingUpdate, MeetingSummary, PaginatedMeetingResponse

from ..utils import extract_plain_text

router = APIRouter(prefix="/meetings", tags=["Meetings"])

@router.get("/", response_model=PaginatedMeetingResponse)
def get_meetings(
    is_academic: bool,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    with Session(engine) as session:
        # 1. Get Total Count for pagination math on frontend
        count_statement = select(func.count()).select_from(Meeting).where(Meeting.is_academic == is_academic)
        total_count = session.exec(count_statement).one()

        # 2. Get Paginated Data
        offset = (page - 1) * limit
        data_statement = (
            select(Meeting)
            .where(Meeting.is_academic == is_academic)
            .order_by(desc(Meeting.meeting_date))
            .offset(offset)
            .limit(limit)
        )
        results = session.exec(data_statement).all()
        
        # 3. Transform to Plain Text
        summaries = [
            MeetingSummary(
                id=m.id,
                serial_num=m.serial_num,
                title_plain=extract_plain_text(m.title),
                meeting_date=m.meeting_date or datetime.now(),
                is_finished=m.is_finished
            ) for m in results
        ]
            
        return {
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "data": summaries
        }

@router.get("/{meeting_id}", response_model=Meeting)
def get_meeting_details(
    meeting_id: uuid_pkg.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    meeting = session.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=404, 
            detail="Meeting not found. It might have been deleted."
        )
    return meeting

@router.patch("/{meeting_id}", response_model=Meeting)
def update_meeting(
    meeting_id: uuid_pkg.UUID,
    meeting_data: MeetingUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # 1. Check Permissions (Only Staff or Admin)
    if current_user.role not in [UserRole.admin, UserRole.staff]:
        raise HTTPException(
            status_code=403,
            detail="Permission denied. Only Staff or Admins can modify meetings."
        )

    # 2. Fetch existing meeting
    db_meeting = session.get(Meeting, meeting_id)
    if not db_meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    # 3. Check Uniqueness (serial_num + is_academic)
    # Only check if one of these fields is actually being changed
    new_serial = meeting_data.serial_num if meeting_data.serial_num is not None else db_meeting.serial_num
    new_type = meeting_data.is_academic if meeting_data.is_academic is not None else db_meeting.is_academic
    
    if meeting_data.serial_num is not None or meeting_data.is_academic is not None:
        statement = select(Meeting).where(
            Meeting.serial_num == new_serial,
            Meeting.is_academic == new_type,
            Meeting.id != meeting_id # Exclude the current meeting
        )
        existing = session.exec(statement).first()
        if existing:
            type_str = "Academic" if new_type else "Syndicate"
            raise HTTPException(
                status_code=400,
                detail=f"Meeting #{new_serial} already exists for {type_str} Council."
            )

    # 4. Apply Updates
    update_dict = meeting_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_meeting, key, value)

    session.add(db_meeting)
    session.commit()
    session.refresh(db_meeting)
    return db_meeting