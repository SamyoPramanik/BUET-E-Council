"""
api/agendas.py
==============
All endpoints for Agendum (agenda items) and their file annexures.

Permission model
────────────────
  viewer  → GET only
  staff   → GET + POST + PATCH + DELETE
  admin   → same as staff (extend here if you add admin-only actions later)

PDF generation
──────────────
  A real implementation would use WeasyPrint, ReportLab, or an HTML→PDF
  service.  The stub below writes a placeholder text file so the endpoint
  works end-to-end without extra dependencies.  Replace `_generate_pdf`
  with your real renderer when ready.
"""

import os
import shutil
import uuid as uuid_pkg
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select, col

from app.database import get_session
from app.dependencies import get_current_user
from app.models import (
    Agendum, AgendumAnnexure, Meeting, Resolution,
    ResolutionAttachment, UploadedFile, User, UserRole,
)
from app.schemas.agendas import (
    AgendumCreate, AgendumPDFResponse, AgendumResponse,
    AgendumUpdate, AnnexureAdd, AnnexureReorder,
)

router = APIRouter(prefix="/agendas", tags=["Agendas"])

# ── helpers ──────────────────────────────────────────────────────────────────

MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", "media"))


def _require_modifier(user: User) -> None:
    """Raise 403 if the user is a viewer."""
    if user.role == UserRole.viewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewers cannot modify agenda items.",
        )


def _get_agendum_or_404(agendum_id: uuid_pkg.UUID, session: Session) -> Agendum:
    ag = session.get(Agendum, agendum_id)
    if not ag:
        raise HTTPException(status_code=404, detail="Agendum not found.")
    return ag


def _build_response(ag: Agendum, session: Session) -> AgendumResponse:
    """Eagerly load annexures + resolution and return the response schema."""
    from app.schemas.agendas import AnnexureResponse, InlineResolutionResponse
    from app.schemas.resolutions import ResolutionAttachmentResponse

    # annexures ordered by `order` asc
    ann_rows = session.exec(
        select(AgendumAnnexure, UploadedFile)
        .join(
            UploadedFile, 
            # Fix: Wrap the FK in col() to define the join clause
            col(AgendumAnnexure.file_id) == UploadedFile.id
        )
        .where(col(AgendumAnnexure.agendum_id) == ag.id)
        # Fix: Wrap the order attribute in col()
        .order_by(col(AgendumAnnexure.order))
    ).all()

    annexures = [
        AnnexureResponse(
            id=ann.id,
            file_id=f.id,
            order=ann.order,
            original_filename=f.original_filename,
            mime_type=f.mime_type,
            size_bytes=f.size_bytes,
            path=f.path,
        )
        for ann, f in ann_rows
    ]

    # resolution (if exists)
    res_row = session.exec(
        select(Resolution).where(Resolution.agendum_id == ag.id)
    ).first()

    resolution = None
    if res_row:
        att_rows = session.exec(
            select(ResolutionAttachment, UploadedFile)
            .join(
                UploadedFile, 
                # Fix: Using col() defines the SQL join condition
                col(ResolutionAttachment.file_id) == UploadedFile.id
            )
            .where(col(ResolutionAttachment.resolution_id) == res_row.id)
            # Fix: Using col() for ordering
            .order_by(col(ResolutionAttachment.order))
        ).all()
        resolution = InlineResolutionResponse(
            id=res_row.id,
            body=res_row.body,
            created_at=res_row.created_at,
            updated_at=res_row.updated_at,
            attachments=[
                ResolutionAttachmentResponse(
                    id=att.id, file_id=f.id, order=att.order,
                    original_filename=f.original_filename,
                    mime_type=f.mime_type, size_bytes=f.size_bytes, path=f.path,
                )
                for att, f in att_rows
            ],
        )

    return AgendumResponse(
        id=ag.id,
        serial=ag.serial,
        body=ag.body,
        is_supplementary=ag.is_supplementary,
        created_at=ag.created_at,
        updated_at=ag.updated_at,
        meeting_id=ag.meeting_id,
        annexures=annexures,
        resolution=resolution,
    )


def _delete_agendum_cascade(ag: Agendum, session: Session) -> None:
    """Delete agendum + its resolution + all attached files (disk + DB)."""
    # 1. resolution attachments
    res = session.exec(
        select(Resolution).where(Resolution.agendum_id == ag.id)
    ).first()
    if res:
        atts = session.exec(
            select(ResolutionAttachment).where(ResolutionAttachment.resolution_id == res.id)
        ).all()
        for att in atts:
            f = session.get(UploadedFile, att.file_id)
            if f:
                _delete_file_from_disk(f)
                session.delete(f)
            session.delete(att)
        session.delete(res)

    # 2. agendum annexures
    anns = session.exec(
        select(AgendumAnnexure).where(AgendumAnnexure.agendum_id == ag.id)
    ).all()
    for ann in anns:
        f = session.get(UploadedFile, ann.file_id)
        if f:
            _delete_file_from_disk(f)
            session.delete(f)
        session.delete(ann)

    session.delete(ag)


def _delete_file_from_disk(f: UploadedFile) -> None:
    try:
        path = MEDIA_ROOT / f.path
        if path.exists():
            path.unlink()
    except Exception:
        pass  # log in production; don't crash the request


def _generate_pdf(content: str, dest_path: Path) -> None:
    """
    Stub PDF generator — replace with WeasyPrint / ReportLab.
    Currently writes a UTF-8 text file so the endpoint is testable now.
    """
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(content, encoding="utf-8")


# ════════════════════════════════════════════════════════════════════════════
# GET /agendas/
# ════════════════════════════════════════════════════════════════════════════

@router.get("/", response_model=List[AgendumResponse])
def list_agendas(
    meeting_id:       uuid_pkg.UUID,
    is_supplementary: Optional[bool] = Query(default=None),
    session:          Session        = Depends(get_session),
    current_user:     User           = Depends(get_current_user),
):
    """
    Return all agenda items for a meeting, ordered by serial.
    Optionally filter by is_supplementary=true|false.
    Each item includes its annexures and resolution (if any).

    200 — list (may be empty)
    404 — meeting not found
    """
    if not session.get(Meeting, meeting_id):
        raise HTTPException(status_code=404, detail="Meeting not found.")

    stmt = select(Agendum).where(Agendum.meeting_id == meeting_id)
    if is_supplementary is not None:
        stmt = stmt.where(Agendum.is_supplementary == is_supplementary)
    stmt = stmt.order_by(col(Agendum.serial))

    agendas = session.exec(stmt).all()
    return [_build_response(ag, session) for ag in agendas]


# ════════════════════════════════════════════════════════════════════════════
# POST /agendas/
# ════════════════════════════════════════════════════════════════════════════

@router.post("/", response_model=AgendumResponse, status_code=status.HTTP_201_CREATED)
def create_agendum(
    data:         AgendumCreate,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Create a blank agenda item under a meeting.

    201 — created
    400 — duplicate serial within the same meeting + is_supplementary group
    403 — viewer attempting to write
    404 — meeting not found
    """
    _require_modifier(current_user)

    if not session.get(Meeting, data.meeting_id):
        raise HTTPException(status_code=404, detail="Meeting not found.")

    # Uniqueness is scoped to (meeting_id, serial, is_supplementary).
    # Serial 1 in regular agendas and serial 1 in supplementary agendas are
    # two different items and must both be allowed.
    existing = session.exec(
        select(Agendum).where(
            Agendum.meeting_id      == data.meeting_id,
            Agendum.serial          == data.serial,
            Agendum.is_supplementary == data.is_supplementary,
        )
    ).first()
    if existing:
        kind = "supplementary" if data.is_supplementary else "regular"
        raise HTTPException(
            status_code=400,
            detail=f"Serial #{data.serial} already exists in {kind} agendas for this meeting.",
        )

    ag = Agendum(
        meeting_id=data.meeting_id,
        serial=data.serial,
        is_supplementary=data.is_supplementary,
    )
    session.add(ag)
    session.commit()
    session.refresh(ag)
    return _build_response(ag, session)


# ════════════════════════════════════════════════════════════════════════════
# PATCH /agendas/{agendum_id}
# ════════════════════════════════════════════════════════════════════════════

@router.patch("/{agendum_id}", response_model=AgendumResponse)
def update_agendum(
    agendum_id:   uuid_pkg.UUID,
    data:         AgendumUpdate,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Partial update: body, serial, is_supplementary.
    At least one field must be provided.

    200 — updated
    400 — no fields provided | duplicate serial
    403 — viewer
    404 — agendum not found
    """
    _require_modifier(current_user)
    ag = _get_agendum_or_404(agendum_id, session)

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=400, detail="At least one field must be provided."
        )

    # if serial is changing, check uniqueness within the meeting
    # Inside update_agendum, replace the conflict check with:
    if "serial" in updates and updates["serial"] != ag.serial:
        conflict = session.exec(
            select(Agendum).where(
                Agendum.meeting_id       == ag.meeting_id,
                Agendum.serial           == updates["serial"],
                Agendum.is_supplementary == ag.is_supplementary,  # ← add this
                Agendum.id               != ag.id,
            )
        ).first()
        if conflict:
            kind = "supplementary" if ag.is_supplementary else "regular"
            raise HTTPException(
                status_code=400,
                detail=f"Serial #{updates['serial']} already exists in {kind} agendas for this meeting.",
            )

    for k, v in updates.items():
        setattr(ag, k, v)
    ag.updated_at = datetime.now(timezone.utc)

    session.add(ag)
    session.commit()
    session.refresh(ag)
    return _build_response(ag, session)


# ════════════════════════════════════════════════════════════════════════════
# DELETE /agendas/{agendum_id}
# ════════════════════════════════════════════════════════════════════════════

@router.delete("/{agendum_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agendum(
    agendum_id:   uuid_pkg.UUID,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Delete one agendum and cascade: its resolution + all attached files.

    204 — deleted
    403 — viewer
    404 — not found
    """
    _require_modifier(current_user)
    ag = _get_agendum_or_404(agendum_id, session)
    _delete_agendum_cascade(ag, session)
    session.commit()


# ════════════════════════════════════════════════════════════════════════════
# DELETE /agendas/?meeting_id=  — delete ALL agendas under a meeting
# ════════════════════════════════════════════════════════════════════════════

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_agendas(
    meeting_id:   uuid_pkg.UUID,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Delete every agenda item (and their resolutions + files) for a meeting.

    204 — deleted (idempotent — returns 204 even if meeting had no agendas)
    403 — viewer
    404 — meeting not found
    """
    _require_modifier(current_user)
    if not session.get(Meeting, meeting_id):
        raise HTTPException(status_code=404, detail="Meeting not found.")

    agendas = session.exec(
        select(Agendum).where(Agendum.meeting_id == meeting_id)
    ).all()
    for ag in agendas:
        _delete_agendum_cascade(ag, session)
    session.commit()


# ════════════════════════════════════════════════════════════════════════════
# FILE ANNEXURES
# ════════════════════════════════════════════════════════════════════════════

@router.post(
    "/{agendum_id}/files",
    response_model=AgendumResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_file_to_agendum(
    agendum_id:   uuid_pkg.UUID,
    data:         AnnexureAdd,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Attach an already-uploaded file to an agendum.
    The UploadedFile record must already exist (created by your upload endpoint).

    201 — attached
    400 — file already attached to this agendum
    403 — viewer
    404 — agendum or file not found
    """
    _require_modifier(current_user)
    ag = _get_agendum_or_404(agendum_id, session)

    if not session.get(UploadedFile, data.file_id):
        raise HTTPException(status_code=404, detail="File not found.")

    # prevent duplicate attachment
    existing = session.exec(
        select(AgendumAnnexure).where(
            AgendumAnnexure.agendum_id == ag.id,
            AgendumAnnexure.file_id    == data.file_id,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="This file is already attached to the agendum."
        )

    ann = AgendumAnnexure(agendum_id=ag.id, file_id=data.file_id, order=data.order)
    session.add(ann)
    session.commit()
    return _build_response(ag, session)


@router.patch(
    "/{agendum_id}/files/{annexure_id}",
    response_model=AgendumResponse,
)
def reorder_agendum_file(
    agendum_id:   uuid_pkg.UUID,
    annexure_id:  uuid_pkg.UUID,
    data:         AnnexureReorder,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Change the display order of one annexure.

    200 — updated
    403 — viewer
    404 — agendum or annexure not found
    """
    _require_modifier(current_user)
    ag = _get_agendum_or_404(agendum_id, session)

    ann = session.get(AgendumAnnexure, annexure_id)
    if not ann or ann.agendum_id != ag.id:
        raise HTTPException(status_code=404, detail="Annexure not found.")

    ann.order = data.order
    session.add(ann)
    session.commit()
    return _build_response(ag, session)


@router.delete(
    "/{agendum_id}/files/{annexure_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_file_from_agendum(
    agendum_id:   uuid_pkg.UUID,
    annexure_id:  uuid_pkg.UUID,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Detach one file from an agendum and delete it from disk + DB.

    204 — deleted
    403 — viewer
    404 — agendum or annexure not found
    """
    _require_modifier(current_user)
    ag = _get_agendum_or_404(agendum_id, session)

    ann = session.get(AgendumAnnexure, annexure_id)
    if not ann or ann.agendum_id != ag.id:
        raise HTTPException(status_code=404, detail="Annexure not found.")

    f = session.get(UploadedFile, ann.file_id)
    if f:
        _delete_file_from_disk(f)
        session.delete(f)
    session.delete(ann)
    session.commit()


@router.delete(
    "/{agendum_id}/files",
    status_code=status.HTTP_204_NO_CONTENT,
)
def clear_all_agendum_files(
    agendum_id:   uuid_pkg.UUID,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Remove all files attached to an agendum.

    204 — cleared (idempotent)
    403 — viewer
    404 — agendum not found
    """
    _require_modifier(current_user)
    ag = _get_agendum_or_404(agendum_id, session)

    anns = session.exec(
        select(AgendumAnnexure).where(AgendumAnnexure.agendum_id == ag.id)
    ).all()
    for ann in anns:
        f = session.get(UploadedFile, ann.file_id)
        if f:
            _delete_file_from_disk(f)
            session.delete(f)
        session.delete(ann)
    session.commit()


# ════════════════════════════════════════════════════════════════════════════
# PDF  (per agendum)
# ════════════════════════════════════════════════════════════════════════════

@router.get("/{agendum_id}/pdf")
def download_agendum_pdf(
    agendum_id:   uuid_pkg.UUID,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Generate (if not yet generated) and download the PDF for one agendum.

    200 — PDF file stream
    404 — agendum not found
    """
    ag = _get_agendum_or_404(agendum_id, session)

    pdf_rel  = f"meetings/{ag.meeting_id}/agendum/{ag.id}/agendum_{ag.serial}.pdf"
    pdf_path = MEDIA_ROOT / pdf_rel

    if not pdf_path.exists():
        content = (
            f"Agendum #{ag.serial}\n"
            f"Supplementary: {ag.is_supplementary}\n\n"
            f"{ag.body or '(no body)'}"
        )
        _generate_pdf(content, pdf_path)

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"agendum_{ag.serial}.pdf",
    )


@router.delete("/{agendum_id}/pdf", response_model=AgendumPDFResponse)
def clear_agendum_pdf(
    agendum_id:   uuid_pkg.UUID,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Delete the cached PDF for an agendum so it will be regenerated next GET.

    200 — cleared (pdf_path will be null in response)
    403 — viewer
    404 — agendum not found
    """
    _require_modifier(current_user)
    ag = _get_agendum_or_404(agendum_id, session)

    pdf_path = MEDIA_ROOT / f"meetings/{ag.meeting_id}/agendum/{ag.id}/agendum_{ag.serial}.pdf"
    if pdf_path.exists():
        pdf_path.unlink()

    return AgendumPDFResponse(agendum_id=ag.id, pdf_path=None)