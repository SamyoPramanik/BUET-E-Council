import uuid as uuid_pkg
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import get_admin_user
from app.models import ParticipantCard, User, Department, Faculty
from ..schemas.participants import (
    ParticipantRead, ParticipantCreate, ParticipantUpdate,
)

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
        role=card.role,
        email=card.email,
        is_external=card.is_external,
        department_id=dept.id if dept else None,
        department=(dept.name_english or dept.name_bangla) if dept else None,
        faculty_id=faculty.id if faculty else None,
        faculty=(faculty.name_english or faculty.name_bangla) if faculty else None,
    )


def _get_participant_or_404(participant_id: uuid_pkg.UUID, session: Session) -> ParticipantCard:
    card = session.get(ParticipantCard, participant_id)
    if not card:
        raise HTTPException(status_code=404, detail="Participant not found.")
    return card


# ════════════════════════════════════════════════════════════════════════════
# GET /participants — open to any signed-in user
# ════════════════════════════════════════════════════════════════════════════

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


# ════════════════════════════════════════════════════════════════════════════
# PARTICIPANT DIRECTORY — admin-only writes.
#
# This is the master list of people (professors, deans, external guests, …)
# that meetings draw their attendee list from. Only admins may add, edit, or
# delete entries here; staff can only attach/detach *existing* entries to a
# specific meeting via PATCH /meetings/{id}/participants (also admin-only —
# see api/meetings.py — staff cannot change who is on a meeting's list).
# ════════════════════════════════════════════════════════════════════════════

@router.post("/participants", response_model=ParticipantRead, status_code=status.HTTP_201_CREATED)
def create_participant(
    data: ParticipantCreate,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user),
):
    """Admin-only: add a new participant card to the directory."""
    if not session.get(Department, data.department_id):
        raise HTTPException(status_code=404, detail="Department not found.")

    card = ParticipantCard(**data.model_dump())
    session.add(card)
    session.commit()
    session.refresh(card)

    dept_by_id, faculty_by_id = build_org_lookup_maps(session)
    return participant_to_read(card, dept_by_id, faculty_by_id)


@router.patch("/participants/{participant_id}", response_model=ParticipantRead)
def update_participant(
    participant_id: uuid_pkg.UUID,
    data: ParticipantUpdate,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user),
):
    """Admin-only: edit a participant card in the directory."""
    card = _get_participant_or_404(participant_id, session)

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="At least one field must be provided.")

    if "department_id" in updates and not session.get(Department, updates["department_id"]):
        raise HTTPException(status_code=404, detail="Department not found.")

    for k, v in updates.items():
        setattr(card, k, v)

    session.add(card)
    session.commit()
    session.refresh(card)

    dept_by_id, faculty_by_id = build_org_lookup_maps(session)
    return participant_to_read(card, dept_by_id, faculty_by_id)


@router.delete("/participants/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_participant(
    participant_id: uuid_pkg.UUID,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user),
):
    """Admin-only: remove a participant card from the directory (also drops it from any meetings)."""
    card = _get_participant_or_404(participant_id, session)
    session.delete(card)
    session.commit()
