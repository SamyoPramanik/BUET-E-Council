"""
api/signature_cards.py
======================
All endpoints for SignatureCard global CRUD + per-meeting assignment.

Endpoints
─────────
  Global catalogue
  ────────────────
  GET    /signature-cards/              list + search (paginated, lazy-load ready)
  POST   /signature-cards/              create a new signature card
  PATCH  /signature-cards/{id}          update content
  DELETE /signature-cards/{id}          delete globally (removes from all meetings)

  Per-meeting assignment
  ──────────────────────
  GET    /meetings/{id}/signature-cards          list cards attached to a meeting (ordered)
  POST   /meetings/{id}/signature-cards          attach an existing card (by id + order)
  PATCH  /meetings/{id}/signature-cards/{sig_id} change display order
  DELETE /meetings/{id}/signature-cards/{sig_id} detach one card from this meeting
  DELETE /meetings/{id}/signature-cards          detach ALL cards from this meeting
"""

import uuid as uuid_pkg
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, col, func, select

from app.database import get_session
from app.dependencies import get_current_user
from app.models import Meeting, MeetingSignatureLink, SignatureCard, User, UserRole
from app.schemas.signature_cards import (
    MeetingSignatureAdd,
    MeetingSignatureReorder,
    PaginatedSignatureCardResponse,
    SignatureCardCreate,
    SignatureCardResponse,
    SignatureCardUpdate,
)

# ── Two routers — one for global CRUD, one mounted under /meetings ────────────
router          = APIRouter(prefix="/signature-cards", tags=["Signature Cards"])
meetings_router = APIRouter(prefix="/meetings",        tags=["Signature Cards"])


# ── helpers ──────────────────────────────────────────────────────────────────

def _require_modifier(user: User) -> None:
    if user.role == UserRole.viewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Only Staff or Admins can modify signature cards.",
        )


def _get_card_or_404(card_id: uuid_pkg.UUID, session: Session) -> SignatureCard:
    card = session.get(SignatureCard, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Signature card not found.")
    return card


def _get_meeting_or_404(meeting_id: uuid_pkg.UUID, session: Session) -> Meeting:
    m = session.get(Meeting, meeting_id)
    if not m:
        raise HTTPException(status_code=404, detail="Meeting not found.")
    return m


def _get_link_or_404(
    meeting_id: uuid_pkg.UUID,
    sig_id:     uuid_pkg.UUID,
    session:    Session,
) -> MeetingSignatureLink:
    link = session.exec(
        select(MeetingSignatureLink).where(
            MeetingSignatureLink.meeting_id        == meeting_id,
            MeetingSignatureLink.signature_card_id == sig_id,
        )
    ).first()
    if not link:
        raise HTTPException(
            status_code=404,
            detail="Signature card is not attached to this meeting.",
        )
    return link


# ════════════════════════════════════════════════════════════════════════════
# GLOBAL CATALOGUE
# ════════════════════════════════════════════════════════════════════════════

@router.get("/", response_model=PaginatedSignatureCardResponse)
def list_signature_cards(
    search:       Optional[str] = Query(default=None, description="Substring search on content"),
    page:         int           = Query(default=1,  ge=1),
    limit:        int           = Query(default=20, ge=1, le=200),
    session:      Session       = Depends(get_session),
    current_user: User          = Depends(get_current_user),
):
    """
    List all signature cards, optionally filtered by a substring in `content`.
    Supports cursor-style lazy loading via `page` + `limit`.

    200 — paginated list (may be empty)
    """
    stmt = select(SignatureCard)
    count_stmt = select(func.count()).select_from(SignatureCard)

    if search:
        pattern = f"%{search.strip()}%"
        stmt       = stmt.where(col(SignatureCard.content).ilike(pattern))
        count_stmt = count_stmt.where(col(SignatureCard.content).ilike(pattern))

    total_count = session.exec(count_stmt).one()
    offset      = (page - 1) * limit

    cards = session.exec(
        stmt.order_by(col(SignatureCard.content))
            .offset(offset)
            .limit(limit)
    ).all()

    return PaginatedSignatureCardResponse(
        total_count=total_count,
        page=page,
        limit=limit,
        data=[SignatureCardResponse.model_validate(c) for c in cards],
    )


@router.post(
    "/",
    response_model=SignatureCardResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_signature_card(
    data:         SignatureCardCreate,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Create a new signature card in the global catalogue.

    201 — created
    400 — duplicate content already exists
    403 — viewer
    """
    _require_modifier(current_user)

    # Prevent exact duplicates in the global catalogue
    existing = session.exec(
        select(SignatureCard).where(SignatureCard.content == data.content.strip())
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="A signature card with this exact content already exists.",
        )

    card = SignatureCard(content=data.content.strip())
    session.add(card)
    session.commit()
    session.refresh(card)
    return SignatureCardResponse.model_validate(card)


@router.patch("/{card_id}", response_model=SignatureCardResponse)
def update_signature_card(
    card_id:      uuid_pkg.UUID,
    data:         SignatureCardUpdate,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Update the content of a signature card.

    200 — updated
    400 — no fields provided | duplicate content
    403 — viewer
    404 — not found
    """
    _require_modifier(current_user)
    card = _get_card_or_404(card_id, session)

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="At least one field must be provided.")

    if "content" in updates:
        new_content = updates["content"].strip()
        if new_content != card.content:
            conflict = session.exec(
                select(SignatureCard).where(
                    SignatureCard.content == new_content,
                    SignatureCard.id      != card_id,
                )
            ).first()
            if conflict:
                raise HTTPException(
                    status_code=400,
                    detail="A signature card with this exact content already exists.",
                )
        updates["content"] = new_content

    for k, v in updates.items():
        setattr(card, k, v)

    session.add(card)
    session.commit()
    session.refresh(card)
    return SignatureCardResponse.model_validate(card)


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_signature_card(
    card_id:      uuid_pkg.UUID,
    session:      Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """
    Delete a signature card from the global catalogue.
    Also removes all meeting–card associations (cascade via junction rows).

    204 — deleted
    403 — viewer
    404 — not found
    """
    _require_modifier(current_user)
    card = _get_card_or_404(card_id, session)

    # Remove junction rows first to avoid FK constraint errors
    links = session.exec(
        select(MeetingSignatureLink).where(
            MeetingSignatureLink.signature_card_id == card_id
        )
    ).all()
    for link in links:
        session.delete(link)

    session.delete(card)
    session.commit()

