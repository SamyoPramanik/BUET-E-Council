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

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlmodel import Session, desc, func, select, col

from app.database import engine, get_session
from app.dependencies import get_current_user
from app.models import Agendum, Meeting, Resolution, User, UserRole
from app.schemas.meetings import (
    MeetingPDFResponse, MeetingSummary,
    MeetingUpdate, PaginatedMeetingResponse,
)

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


# ════════════════════════════════════════════════════════════════════════════
# PDF — AGENDA
# ════════════════════════════════════════════════════════════════════════════

@router.get("/{meeting_id}/pdf/agenda")
def download_meeting_agenda_pdf(
    meeting_id:   uuid_pkg.UUID,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Generate (once, cached) and stream the full agenda PDF.
    Covers every agenda item ordered by serial, supplementary items last.

    200 — PDF | 404 — meeting not found
    """
    meeting  = _get_meeting_or_404(meeting_id, session)
    pdf_rel  = f"meetings/{meeting_id}/full_agenda.pdf"
    pdf_path = MEDIA_ROOT / pdf_rel

    if not pdf_path.exists():
        agendas = session.exec(
            select(Agendum)
            .where(col(Agendum.meeting_id) == meeting_id) # Fix: Define the filter clause
            .order_by(
                col(Agendum.is_supplementary), # Fix: Define the first order column
                col(Agendum.serial)            # Fix: Define the second order column
            )
        ).all()

        lines = [
            f"Meeting #{meeting.serial_num}",
            f"Title   : {meeting.title}",
            f"Date    : {meeting.meeting_date}",
            "",
            "=" * 60,
            "A G E N D A",
            "=" * 60,
        ]
        for ag in agendas:
            prefix = "[Supplementary] " if ag.is_supplementary else ""
            lines += ["", f"{ag.serial}. {prefix}", ag.body or "(no body yet)"]

        _generate_pdf("\n".join(lines), pdf_path)
        meeting.agenda_pdf = pdf_rel
        session.add(meeting)
        session.commit()

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"agenda_meeting_{meeting.serial_num}.pdf",
    )


@router.delete("/{meeting_id}/pdf/agenda", response_model=MeetingPDFResponse)
def clear_meeting_agenda_pdf(
    meeting_id:   uuid_pkg.UUID,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Clear cached agenda PDF — next GET will regenerate it.
    200 — cleared | 403 — viewer | 404 — not found
    """
    _require_modifier(current_user)
    meeting = _get_meeting_or_404(meeting_id, session)

    if meeting.agenda_pdf:
        p = MEDIA_ROOT / meeting.agenda_pdf
        if p.exists():
            p.unlink()
        meeting.agenda_pdf = None
        session.add(meeting)
        session.commit()

    return MeetingPDFResponse(
        meeting_id=meeting.id,
        agenda_pdf=None,
        resolution_pdf=meeting.resolution_pdf,
    )


# ════════════════════════════════════════════════════════════════════════════
# PDF — RESOLUTION
# ════════════════════════════════════════════════════════════════════════════

@router.get("/{meeting_id}/pdf/resolution")
def download_meeting_resolution_pdf(
    meeting_id:   uuid_pkg.UUID,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Generate (once, cached) and stream the full resolution PDF.
    Only agendas that have a resolution are included.

    200 — PDF | 404 — meeting not found
    """
    meeting  = _get_meeting_or_404(meeting_id, session)
    pdf_rel  = f"meetings/{meeting_id}/full_resolution.pdf"
    pdf_path = MEDIA_ROOT / pdf_rel

    if not pdf_path.exists():
        agendas = session.exec(
            select(Agendum)
            .where(Agendum.meeting_id == meeting_id)
            .order_by(col(Agendum.serial))
        ).all()

        lines = [
            f"Meeting #{meeting.serial_num}",
            f"Title   : {meeting.title}",
            f"Date    : {meeting.meeting_date}",
            "",
            "=" * 60,
            "R E S O L U T I O N S",
            "=" * 60,
        ]
        for ag in agendas:
            res = session.exec(
                select(Resolution).where(Resolution.agendum_id == ag.id)
            ).first()
            if not res:
                continue
            lines += ["", f"Agendum #{ag.serial}", res.body or "(no resolution body)"]

        _generate_pdf("\n".join(lines), pdf_path)
        meeting.resolution_pdf = pdf_rel
        session.add(meeting)
        session.commit()

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"resolution_meeting_{meeting.serial_num}.pdf",
    )


@router.delete("/{meeting_id}/pdf/resolution", response_model=MeetingPDFResponse)
def clear_meeting_resolution_pdf(
    meeting_id:   uuid_pkg.UUID,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Clear cached resolution PDF — next GET will regenerate it.
    200 — cleared | 403 — viewer | 404 — not found
    """
    _require_modifier(current_user)
    meeting = _get_meeting_or_404(meeting_id, session)

    if meeting.resolution_pdf:
        p = MEDIA_ROOT / meeting.resolution_pdf
        if p.exists():
            p.unlink()
        meeting.resolution_pdf = None
        session.add(meeting)
        session.commit()

    return MeetingPDFResponse(
        meeting_id=meeting.id,
        agenda_pdf=meeting.agenda_pdf,
        resolution_pdf=None,
    )