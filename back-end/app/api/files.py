"""
api/files.py
============
File upload endpoint.

POST /files/upload   — upload a single file, returns UploadedFile metadata
DELETE /files/{id}   — delete a file from disk + DB (optional utility)

The binary is stored under MEDIA_ROOT/<year>/<month>/<uuid>_<original_name>.
A UUID-based stored_filename is used to avoid collisions and path traversal.
"""

import os
import uuid as uuid_pkg
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_current_user
from app.models import UploadedFile, User, UserRole

router = APIRouter(prefix="/files", tags=["Files"])

MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", "media"))

# 50 MB hard limit — adjust as needed
MAX_FILE_SIZE = int(os.getenv("MAX_UPLOAD_BYTES", 50 * 1024 * 1024))

ALLOWED_MIME_TYPES = {
    # documents
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    # images
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
    # text / data
    "text/plain",
    "text/csv",
    "application/json",
    # archives
    "application/zip",
    "application/x-zip-compressed",
}


# ── helpers ──────────────────────────────────────────────────────────────────

def _require_modifier(user: User) -> None:
    if user.role == UserRole.viewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewers cannot upload files.",
        )


def _safe_filename(original: str) -> str:
    """Strip directory components and whitespace from the original filename."""
    name = Path(original).name.strip()
    # Replace spaces with underscores so paths stay tidy
    return name.replace(" ", "_") or "unnamed"


def _build_dest_path(stored_filename: str) -> tuple[Path, str]:
    """
    Returns (absolute_path, relative_path_from_MEDIA_ROOT).
    Files are sharded by year/month to keep directory sizes manageable.
    """
    now     = datetime.now(timezone.utc)
    rel_dir = Path("uploads") / str(now.year) / f"{now.month:02d}"
    abs_dir = MEDIA_ROOT / rel_dir
    abs_dir.mkdir(parents=True, exist_ok=True)

    abs_path = abs_dir / stored_filename
    rel_path = str(rel_dir / stored_filename)
    return abs_path, rel_path


# ════════════════════════════════════════════════════════════════════════════
# POST /files/upload
# ════════════════════════════════════════════════════════════════════════════

@router.post(
    "/upload",
    response_model=UploadedFile,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    file:         UploadFile  = File(...),
    session:      Session     = Depends(get_session),
    current_user: User        = Depends(get_current_user),
):
    """
    Upload a single file and persist its metadata.

    Returns the full UploadedFile record (including `id`) which callers
    must pass to POST /agendas/{id}/files or POST /resolutions/{id}/files.

    201 — uploaded
    400 — file too large | unsupported MIME type
    403 — viewer
    """
    _require_modifier(current_user)

    # ── MIME type check ──────────────────────────────────────────────────
    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{content_type}'. "
                f"Allowed types: {', '.join(sorted(ALLOWED_MIME_TYPES))}"
            ),
        )

    # ── Read & size check ────────────────────────────────────────────────
    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=(
                f"File too large ({len(data):,} bytes). "
                f"Maximum allowed size is {MAX_FILE_SIZE:,} bytes "
                f"({MAX_FILE_SIZE // (1024 * 1024)} MB)."
            ),
        )
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # ── Persist to disk ──────────────────────────────────────────────────
    original_name   = _safe_filename(file.filename or "unnamed")
    file_uuid       = uuid_pkg.uuid4()
    # e.g.  a1b2c3d4-..._report.pdf
    stored_filename = f"{file_uuid}_{original_name}"
    abs_path, rel_path = _build_dest_path(stored_filename)

    try:
        abs_path.write_bytes(data)
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not write file to disk: {exc}",
        )

    # ── Persist metadata to DB ───────────────────────────────────────────
    db_file = UploadedFile(
        id=file_uuid,
        original_filename=original_name,
        stored_filename=stored_filename,
        path=rel_path,
        mime_type=content_type,
        size_bytes=len(data),
    )
    session.add(db_file)
    session.commit()
    session.refresh(db_file)
    return db_file


# ════════════════════════════════════════════════════════════════════════════
# DELETE /files/{file_id}   (utility — direct deletion)
# ════════════════════════════════════════════════════════════════════════════

@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id:      uuid_pkg.UUID,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Directly delete a file record + its bytes from disk.

    Note: prefer deleting via the parent resource endpoints
    (DELETE /agendas/{id}/files/{ann_id}) which handle the junction row too.
    This endpoint is a safety valve for orphaned UploadedFile rows.

    204 — deleted
    403 — viewer
    404 — not found
    """
    _require_modifier(current_user)

    db_file = session.get(UploadedFile, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found.")

    # Remove from disk
    try:
        path = MEDIA_ROOT / db_file.path
        if path.exists():
            path.unlink()
    except OSError:
        pass  # log in production; don't block the DB delete

    session.delete(db_file)
    session.commit()