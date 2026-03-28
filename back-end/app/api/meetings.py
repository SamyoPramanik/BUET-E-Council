"""
api/meetings.py
===============
Meeting CRUD + participant assignment + meeting-level PDF generation.

PDF endpoints
─────────────
  GET    /meetings/{id}/pdf/agenda       generate (once) + download full agenda PDF
  GET    /meetings/{id}/pdf/resolution   generate (once) + download full resolution PDF
  DELETE /meetings/{id}/pdf/agenda       clear cached PDF → triggers regen on next GET
  DELETE /meetings/{id}/pdf/resolution   same for resolution
"""

import os
import uuid as uuid_pkg
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlmodel import Session, desc, func, select, col

from app.database import engine, get_session
from app.dependencies import get_current_user
from app.models import Agendum, Meeting, Resolution, User, UserRole, UploadedFile
from app.schemas.meetings import (
    MeetingPDFResponse, MeetingSummary,
    MeetingUpdate, PaginatedMeetingResponse,
)
from app.api.files import upload_file, delete_file

router = APIRouter(prefix="/meetings", tags=["Meetings"])

MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", "media"))


# ── helpers ──────────────────────────────────────────────────────────────────

def _require_modifier(user: User) -> None:
    if user.role == UserRole.viewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Only Staff or Admins can modify meetings.",
        )


def _get_meeting_or_404(meeting_id: uuid_pkg.UUID, session: Session) -> Meeting:
    m = session.get(Meeting, meeting_id)
    if not m:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found. It might have been deleted.",
        )
    return m


def _generate_pdf(content: str, dest_path: Path) -> None:
    """Stub renderer — replace with WeasyPrint / ReportLab when ready."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(content, encoding="utf-8")


# ════════════════════════════════════════════════════════════════════════════
# GET /meetings/
# ════════════════════════════════════════════════════════════════════════════

@router.get("/", response_model=PaginatedMeetingResponse)
def get_meetings(
    is_academic:  bool,
    page:         int  = Query(1, ge=1),
    limit:        int  = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    with Session(engine) as session:
        count_stmt = (
            select(func.count())
            .select_from(Meeting)
            .where(Meeting.is_academic == is_academic)
        )
        total_count = session.exec(count_stmt).one()

        offset    = (page - 1) * limit
        data_stmt = (
            select(Meeting)
            .where(Meeting.is_academic == is_academic)
            .order_by(desc(Meeting.meeting_date))
            .offset(offset)
            .limit(limit)
        )
        results = session.exec(data_stmt).all()

        summaries = [
            MeetingSummary(
                id=m.id,
                serial_num=m.serial_num,
                title_plain=m.title,
                meeting_date=m.meeting_date or datetime.now(timezone.utc),
                is_finished=m.is_finished,
            )
            for m in results
        ]

        return {"total_count": total_count, "page": page, "limit": limit, "data": summaries}


# ════════════════════════════════════════════════════════════════════════════
# GET /meetings/{meeting_id}
# ════════════════════════════════════════════════════════════════════════════

@router.get("/{meeting_id}", response_model=Meeting)
def get_meeting_details(
    meeting_id:   uuid_pkg.UUID,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """200 — full record | 404 — not found"""
    return _get_meeting_or_404(meeting_id, session)


# ════════════════════════════════════════════════════════════════════════════
# PATCH /meetings/{meeting_id}
# ════════════════════════════════════════════════════════════════════════════

@router.patch("/{meeting_id}", response_model=Meeting)
def update_meeting(
    meeting_id:   uuid_pkg.UUID,
    meeting_data: MeetingUpdate,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    200 — updated | 400 — duplicate serial | 403 — viewer | 404 — not found
    """
    _require_modifier(current_user)
    db_meeting = _get_meeting_or_404(meeting_id, session)

    new_serial = meeting_data.serial_num  if meeting_data.serial_num  is not None else db_meeting.serial_num
    new_type   = meeting_data.is_academic if meeting_data.is_academic is not None else db_meeting.is_academic

    if meeting_data.serial_num is not None or meeting_data.is_academic is not None:
        conflict = session.exec(
            select(Meeting).where(
                Meeting.serial_num  == new_serial,
                Meeting.is_academic == new_type,
                Meeting.id          != meeting_id,
            )
        ).first()
        if conflict:
            type_str = "Academic" if new_type else "Syndicate"
            raise HTTPException(
                status_code=400,
                detail=f"Meeting #{new_serial} already exists for {type_str} Council.",
            )

    for key, value in meeting_data.model_dump(exclude_unset=True).items():
        setattr(db_meeting, key, value)

    session.add(db_meeting)
    session.commit()
    session.refresh(db_meeting)
    return db_meeting


# ════════════════════════════════════════════════════════════════════════════
# PARTICIPANTS
# ════════════════════════════════════════════════════════════════════════════

@router.get("/{meeting_id}/participants")
def get_meeting_participants(
    meeting_id:   uuid_pkg.UUID,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """Return full participant list for a meeting."""
    return _get_meeting_or_404(meeting_id, session).members


@router.patch("/{meeting_id}/participants", response_model=Meeting)
def update_meeting_participants(
    meeting_id:      uuid_pkg.UUID,
    participant_ids: list[uuid_pkg.UUID],
    session:         Session = Depends(get_session),
    current_user:    User    = Depends(get_current_user),
):
    """
    Replace the full participant list (pass complete desired list).
    200 — updated | 403 — viewer | 404 — meeting not found
    """
    _require_modifier(current_user)
    from app.models import ParticipantCard

    meeting = _get_meeting_or_404(meeting_id, session)
    meeting.members = list(
        session.exec(
            select(ParticipantCard).where(col(ParticipantCard.id).in_(participant_ids))
        ).all()
    )
    session.add(meeting)
    session.commit()
    session.refresh(meeting)
    return meeting


"""
Paste these endpoints into api/meetings.py, replacing the old
GET/DELETE /pdf/agenda and /pdf/resolution blocks.

Also update models.py Meeting fields:
    agenda_pdf:     Optional[uuid_pkg.UUID] = Field(default=None, nullable=True)
    resolution_pdf: Optional[uuid_pkg.UUID] = Field(default=None, nullable=True)

And add these imports at the top of meetings.py:
    from fastapi import UploadFile, File
    from app.api.files import upload_file, delete_file
    from app.models import UploadedFile
"""

# ════════════════════════════════════════════════════════════════════════════
# AGENDA PDF — UPLOAD + DOWNLOAD + DELETE
# ════════════════════════════════════════════════════════════════════════════

@router.post("/{meeting_id}/files/agenda", response_model=MeetingPDFResponse)
async def upload_agenda_pdf(
    meeting_id: uuid_pkg.UUID,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Upload (or replace) Agenda PDF using central file system"""
    _require_modifier(current_user)
    meeting = _get_meeting_or_404(meeting_id, session)

    # Optional: delete old file first (replace behavior)
    if meeting.agenda_pdf:
        try:
            delete_file(file_id=meeting.agenda_pdf, session=session, current_user=current_user)
        except Exception:
            pass  # old file already gone

    # Upload new file
    uploaded = await upload_file(
        file=file,
        session=session,
        current_user=current_user
    )

    # Link to meeting
    meeting.agenda_pdf = uploaded.id
    session.add(meeting)
    session.commit()
    session.refresh(meeting)

    return MeetingPDFResponse(
        meeting_id=meeting.id,
        agenda_pdf=uploaded.id,
        resolution_pdf=meeting.resolution_pdf,
    )


@router.get("/{meeting_id}/files/agenda")
async def download_agenda_pdf(
    meeting_id: uuid_pkg.UUID,
    session: Session = Depends(get_session),
):
    """Download the uploaded Agenda PDF"""
    meeting = _get_meeting_or_404(meeting_id, session)

    if not meeting.agenda_pdf:
        raise HTTPException(status_code=404, detail="No agenda PDF uploaded yet.")

    uploaded_file = session.get(UploadedFile, meeting.agenda_pdf)
    if not uploaded_file:
        raise HTTPException(status_code=404, detail="File record not found.")

    file_path = MEDIA_ROOT / uploaded_file.path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk.")

    return FileResponse(
        path=str(file_path),
        media_type=uploaded_file.mime_type or "application/pdf",
        filename=uploaded_file.original_filename or f"agenda_meeting_{meeting.serial_num}.pdf",
    )


@router.delete("/{meeting_id}/files/agenda", response_model=MeetingPDFResponse)
def delete_agenda_pdf(
    meeting_id: uuid_pkg.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete Agenda PDF"""
    _require_modifier(current_user)
    meeting = _get_meeting_or_404(meeting_id, session)

    if meeting.agenda_pdf:
        try:
            delete_file(file_id=meeting.agenda_pdf, session=session, current_user=current_user)
        except Exception:
            pass
        meeting.agenda_pdf = None
        session.add(meeting)
        session.commit()

    return MeetingPDFResponse(
        meeting_id=meeting.id,
        agenda_pdf=None,
        resolution_pdf=meeting.resolution_pdf,
    )


# ════════════════════════════════════════════════════════════════════════════
# RESOLUTION PDF — UPLOAD + DOWNLOAD + DELETE
# ════════════════════════════════════════════════════════════════════════════

@router.post("/{meeting_id}/files/resolution", response_model=MeetingPDFResponse)
async def upload_resolution_pdf(
    meeting_id: uuid_pkg.UUID,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Upload (or replace) Resolution PDF using central file system"""
    _require_modifier(current_user)
    meeting = _get_meeting_or_404(meeting_id, session)

    if meeting.resolution_pdf:
        try:
            delete_file(file_id=meeting.resolution_pdf, session=session, current_user=current_user)
        except Exception:
            pass

    uploaded = await upload_file(
        file=file,
        session=session,
        current_user=current_user
    )

    meeting.resolution_pdf = uploaded.id
    session.add(meeting)
    session.commit()
    session.refresh(meeting)

    return MeetingPDFResponse(
        meeting_id=meeting.id,
        agenda_pdf=meeting.agenda_pdf,
        resolution_pdf=uploaded.id,
    )


@router.get("/{meeting_id}/files/resolution")
async def download_resolution_pdf(
    meeting_id: uuid_pkg.UUID,
    session: Session = Depends(get_session),
):
    """Download the uploaded Resolution PDF"""
    meeting = _get_meeting_or_404(meeting_id, session)

    if not meeting.resolution_pdf:
        raise HTTPException(status_code=404, detail="No resolution PDF uploaded yet.")

    uploaded_file = session.get(UploadedFile, meeting.resolution_pdf)
    if not uploaded_file:
        raise HTTPException(status_code=404, detail="File record not found.")

    file_path = MEDIA_ROOT / uploaded_file.path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk.")

    return FileResponse(
        path=str(file_path),
        media_type=uploaded_file.mime_type or "application/pdf",
        filename=uploaded_file.original_filename or f"resolution_meeting_{meeting.serial_num}.pdf",
    )


@router.delete("/{meeting_id}/files/resolution", response_model=MeetingPDFResponse)
def delete_resolution_pdf(
    meeting_id: uuid_pkg.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete Resolution PDF"""
    _require_modifier(current_user)
    meeting = _get_meeting_or_404(meeting_id, session)

    if meeting.resolution_pdf:
        try:
            delete_file(file_id=meeting.resolution_pdf, session=session, current_user=current_user)
        except Exception:
            pass
        meeting.resolution_pdf = None
        session.add(meeting)
        session.commit()

    return MeetingPDFResponse(
        meeting_id=meeting.id,
        agenda_pdf=meeting.agenda_pdf,
        resolution_pdf=None,
    )