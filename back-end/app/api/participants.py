from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, col
from app.database import get_session
from app.models import Meeting, ParticipantCard, UserRole, Department, Faculty
from app.dependencies import get_current_user # Assuming you have an auth helper
from ..schemas.participants import *

router = APIRouter()


def build_org_lookup_maps(session: Session):
    """Department/Faculty lookup maps, built once and reused across a request
    to avoid N+1 queries when serialising a list of ParticipantCards."""
    departments = session.exec(select(Department)).all()
    faculties = session.exec(select(Faculty)).all()
    return {d.id: d for d in departments}, {f.id: f for f in faculties}


def participant_to_read(
    card: ParticipantCard,
    dept_by_id: dict,
    faculty_by_id: dict,
) -> ParticipantRead:
    dept = dept_by_id.get(card.department_id)
    faculty = faculty_by_id.get(dept.faculty_id) if dept else None
    return ParticipantRead(
        id=card.id,
        content=card.content,
        email=card.email,
        department_id=dept.id if dept else None,
        department=(dept.name_english or dept.name_bangla) if dept else None,
        faculty_id=faculty.id if faculty else None,
        faculty=(faculty.name_english or faculty.name_bangla) if faculty else None,
    )


# --- 1st API: Get all Participant Cards ---
@router.get("/participants", response_model=List[ParticipantRead])
def get_all_participants(session: Session = Depends(get_session)):
    """
    Returns a list of all participants, with department/faculty names joined in.
    - 200: Success
    - 500: Database Error
    """
    try:
        participants = session.exec(select(ParticipantCard)).all()
        dept_by_id, faculty_by_id = build_org_lookup_maps(session)
        return [participant_to_read(p, dept_by_id, faculty_by_id) for p in participants]
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


# --- 2nd API: Modify Meeting Participant List ---
@router.patch("/meetings/{meeting_id}/participants")
def update_meeting_members(
    meeting_id: uuid_pkg.UUID,
    data: UpdateMeetingParticipants,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user) # Logic to check user role
):
    """
    Updates the many-to-many relationship for a meeting.
    - 200: Success
    - 403: Forbidden (If user is a Viewer)
    - 404: Meeting or Participant not found
    """
    # 1. Authorization Check
    if current_user.role == UserRole.viewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Viewers are not allowed to modify meeting participants"
        )

    # 2. Fetch the Meeting
    meeting = session.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # 3. Fetch all requested Participant Cards
    statement = select(ParticipantCard).where(col(ParticipantCard.id).in_(data.participant_ids))
    new_members = session.exec(statement).all()

    # Check if all IDs provided actually exist
    if len(new_members) != len(data.participant_ids):
        raise HTTPException(status_code=404, detail="One or more Participant IDs are invalid")

    # 4. Update the Relationship
    # SQLModel handles the Link table automatically when you replace the list
    meeting.members = list(new_members)
    
    session.add(meeting)
    session.commit()
    session.refresh(meeting)

    return {"message": "Participant list updated successfully", "count": len(meeting.members)}

@router.get("/meetings/{meeting_id}/participants", response_model=List[ParticipantRead])
def get_meeting_participants(
    meeting_id: uuid_pkg.UUID, 
    session: Session = Depends(get_session)
):
    """
    Retrieves all ParticipantCards associated with a specific meeting.
    - 200: Success
    - 404: Meeting not found
    """
    # 1. Fetch the meeting first to verify it exists
    meeting = session.get(Meeting, meeting_id)
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # 2. Return the members list 
    # SQLModel automatically handles the Many-to-Many fetch through the relationship
    return meeting.members