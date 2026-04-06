"""
api/resolutions.py
==================
All endpoints for Resolution and their file attachments.

Permissions: same as agendas — viewers GET only, staff/admin write.
"""

import os
import uuid as uuid_pkg
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select, col

from app.database import get_session
from app.dependencies import get_current_user
from app.models import (
    Agendum, Resolution, ResolutionAttachment,
    UploadedFile, User, UserRole,
)
from app.schemas.resolutions import (
    ResolutionAttachmentResponse, ResolutionCreate,
    ResolutionPDFResponse, ResolutionResponse, ResolutionUpdate,
    ResolutionAttachmentAdd, ResolutionAttachmentReorder,
)

router = APIRouter(prefix="/resolutions", tags=["Resolutions"])

MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", "media"))


# ── helpers ──────────────────────────────────────────────────────────────────

def _require_modifier(user: User) -> None:
    if user.role == UserRole.viewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewers cannot modify resolutions.",
        )


def _get_resolution_or_404(resolution_id: uuid_pkg.UUID, session: Session) -> Resolution:
    res = session.get(Resolution, resolution_id)
    if not res:
        raise HTTPException(status_code=404, detail="Resolution not found.")
    return res


def _build_response(res: Resolution, session: Session) -> ResolutionResponse:
    att_rows = session.exec(
        select(ResolutionAttachment, UploadedFile)
        .join(
            UploadedFile, 
            # Use col() to fix the "bool" error in .join()
            col(ResolutionAttachment.file_id) == UploadedFile.id 
        )
        .where(col(ResolutionAttachment.resolution_id) == res.id)
        # Use col() to fix the "int" error in .order_by()
        .order_by(col(ResolutionAttachment.order)) 
    ).all()

    return ResolutionResponse(
        id=res.id,
        body=res.body,
        created_at=res.created_at,
        updated_at=res.updated_at,
        agendum_id=res.agendum_id,
        attachments=[
            ResolutionAttachmentResponse(
                id=att.id, file_id=f.id, order=att.order,
                original_filename=f.original_filename,
                mime_type=f.mime_type, size_bytes=f.size_bytes, path=f.path,
            )
            for att, f in att_rows
        ],
    )


def _delete_file_from_disk(f: UploadedFile) -> None:
    try:
        path = MEDIA_ROOT / f.path
        if path.exists():
            path.unlink()
    except Exception:
        pass


def _generate_pdf(content: str, dest_path: Path) -> None:
    """Stub — replace with WeasyPrint / ReportLab."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(content, encoding="utf-8")


# ════════════════════════════════════════════════════════════════════════════
# POST /resolutions/  — create under an agendum
# ════════════════════════════════════════════════════════════════════════════

@router.post("/", response_model=ResolutionResponse, status_code=status.HTTP_201_CREATED)
def create_resolution(
    data:         ResolutionCreate,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Create a blank resolution tied to an agendum.
    Each agendum can have at most one resolution (enforced by DB UNIQUE on agendum_id).

    201 — created
    400 — resolution already exists for this agendum
    403 — viewer
    404 — agendum not found
    """
    _require_modifier(current_user)

    if not session.get(Agendum, data.agendum_id):
        raise HTTPException(status_code=404, detail="Agendum not found.")

    existing = session.exec(
        select(Resolution).where(Resolution.agendum_id == data.agendum_id)
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="A resolution already exists for this agendum. Use PATCH to update it.",
        )

    res = Resolution(agendum_id=data.agendum_id)
    session.add(res)
    session.commit()
    session.refresh(res)
    return _build_response(res, session)


# ════════════════════════════════════════════════════════════════════════════
# PATCH /resolutions/{resolution_id}
# ════════════════════════════════════════════════════════════════════════════

@router.patch("/{resolution_id}", response_model=ResolutionResponse)
def update_resolution(
    resolution_id: uuid_pkg.UUID,
    data:          ResolutionUpdate,
    session:       Session = Depends(get_session),
    current_user:  User    = Depends(get_current_user),
):
    """
    Update the body of a resolution.

    200 — updated
    400 — no fields provided
    403 — viewer
    404 — resolution not found
    """
    _require_modifier(current_user)
    res = _get_resolution_or_404(resolution_id, session)

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="At least one field must be provided.")

    for k, v in updates.items():
        setattr(res, k, v)
    res.updated_at = datetime.now(timezone.utc)

    session.add(res)
    session.commit()
    session.refresh(res)
    return _build_response(res, session)


# ════════════════════════════════════════════════════════════════════════════
# DELETE /resolutions/{resolution_id}
# ════════════════════════════════════════════════════════════════════════════

@router.delete("/{resolution_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resolution(
    resolution_id: uuid_pkg.UUID,
    session:       Session = Depends(get_session),
    current_user:  User    = Depends(get_current_user),
):
    """
    Delete a resolution and all its attached files.

    204 — deleted
    403 — viewer
    404 — not found
    """
    _require_modifier(current_user)
    res = _get_resolution_or_404(resolution_id, session)

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
    session.commit()


# ════════════════════════════════════════════════════════════════════════════
# FILE ATTACHMENTS
# ════════════════════════════════════════════════════════════════════════════

@router.post(
    "/{resolution_id}/files",
    response_model=ResolutionResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_file_to_resolution(
    resolution_id: uuid_pkg.UUID,
    data:          ResolutionAttachmentAdd,
    session:       Session = Depends(get_session),
    current_user:  User    = Depends(get_current_user),
):
    """
    Attach an already-uploaded file to a resolution.

    201 — attached
    400 — file already attached
    403 — viewer
    404 — resolution or file not found
    """
    _require_modifier(current_user)
    res = _get_resolution_or_404(resolution_id, session)

    if not session.get(UploadedFile, data.file_id):
        raise HTTPException(status_code=404, detail="File not found.")

    existing = session.exec(
        select(ResolutionAttachment).where(
            ResolutionAttachment.resolution_id == res.id,
            ResolutionAttachment.file_id       == data.file_id,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="This file is already attached to the resolution."
        )

    att = ResolutionAttachment(
        resolution_id=res.id, file_id=data.file_id, order=data.order
    )
    session.add(att)
    session.commit()
    return _build_response(res, session)


@router.patch(
    "/{resolution_id}/files/{attachment_id}",
    response_model=ResolutionResponse,
)
def reorder_resolution_file(
    resolution_id: uuid_pkg.UUID,
    attachment_id: uuid_pkg.UUID,
    data:          ResolutionAttachmentReorder,
    session:       Session = Depends(get_session),
    current_user:  User    = Depends(get_current_user),
):
    """
    Change the display order of one attachment.

    200 — updated
    403 — viewer
    404 — resolution or attachment not found
    """
    _require_modifier(current_user)
    res = _get_resolution_or_404(resolution_id, session)

    att = session.get(ResolutionAttachment, attachment_id)
    if not att or att.resolution_id != res.id:
        raise HTTPException(status_code=404, detail="Attachment not found.")

    att.order = data.order
    session.add(att)
    session.commit()
    return _build_response(res, session)


@router.delete(
    "/{resolution_id}/files/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_file_from_resolution(
    resolution_id: uuid_pkg.UUID,
    attachment_id: uuid_pkg.UUID,
    session:       Session = Depends(get_session),
    current_user:  User    = Depends(get_current_user),
):
    """
    Remove and delete one attachment from a resolution.

    204 — deleted
    403 — viewer
    404 — resolution or attachment not found
    """
    _require_modifier(current_user)
    res = _get_resolution_or_404(resolution_id, session)

    att = session.get(ResolutionAttachment, attachment_id)
    if not att or att.resolution_id != res.id:
        raise HTTPException(status_code=404, detail="Attachment not found.")

    f = session.get(UploadedFile, att.file_id)
    if f:
        _delete_file_from_disk(f)
        session.delete(f)
    session.delete(att)
    session.commit()


@router.delete(
    "/{resolution_id}/files",
    status_code=status.HTTP_204_NO_CONTENT,
)
def clear_all_resolution_files(
    resolution_id: uuid_pkg.UUID,
    session:       Session = Depends(get_session),
    current_user:  User    = Depends(get_current_user),
):
    """
    Remove all files attached to a resolution.

    204 — cleared (idempotent)
    403 — viewer
    404 — resolution not found
    """
    _require_modifier(current_user)
    res = _get_resolution_or_404(resolution_id, session)

    atts = session.exec(
        select(ResolutionAttachment).where(ResolutionAttachment.resolution_id == res.id)
    ).all()
    for att in atts:
        f = session.get(UploadedFile, att.file_id)
        if f:
            _delete_file_from_disk(f)
            session.delete(f)
        session.delete(att)
    session.commit()


# ════════════════════════════════════════════════════════════════════════════
# PDF  (per resolution)
# ════════════════════════════════════════════════════════════════════════════

@router.get("/{resolution_id}/pdf")
def download_resolution_pdf(
    resolution_id: uuid_pkg.UUID,
    session:       Session = Depends(get_session),
    current_user:  User    = Depends(get_current_user),
):
    """
    Generate (if not yet cached) and download the PDF for one resolution.

    200 — PDF stream
    404 — resolution not found
    """
    res = _get_resolution_or_404(resolution_id, session)

    pdf_path = MEDIA_ROOT / f"meetings/resolution/{res.id}/resolution.pdf"
    if not pdf_path.exists():
        content = f"Resolution\nAgendum: {res.agendum_id}\n\n{res.body or '(no body)'}"
        _generate_pdf(content, pdf_path)

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename="resolution.pdf",
    )


@router.delete("/{resolution_id}/pdf", response_model=ResolutionPDFResponse)
def clear_resolution_pdf(
    resolution_id: uuid_pkg.UUID,
    session:       Session = Depends(get_session),
    current_user:  User    = Depends(get_current_user),
):
    """
    Delete the cached PDF so it will be regenerated next GET.

    200 — cleared
    403 — viewer
    404 — resolution not found
    """
    _require_modifier(current_user)
    res = _get_resolution_or_404(resolution_id, session)

    pdf_path = MEDIA_ROOT / f"meetings/resolution/{res.id}/resolution.pdf"
    if pdf_path.exists():
        pdf_path.unlink()

    return ResolutionPDFResponse(resolution_id=res.id, pdf_path=None)