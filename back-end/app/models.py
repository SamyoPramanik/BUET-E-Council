"""
models.py  —  BUET meeting management system
=============================================

Root cause of the error
────────────────────────
  `from __future__ import annotations` makes Python treat ALL annotations as
  strings (PEP 563 lazy evaluation).  SQLModel's Relationship() inspects the
  annotation at class-definition time to resolve the target model.  With lazy
  evaluation the annotation arrives as the literal string
  "List['UserSession']" or "Mapped[List['UserSession']]" and SQLAlchemy's
  class registry cannot resolve either.

  Fix: remove `from __future__ import annotations` entirely.
  Use plain `List[...]` / `Optional[...]` from `typing` — SQLModel handles
  these correctly without Mapped[].

  Do NOT use `from sqlalchemy.orm import Mapped` with SQLModel Relationship().
  Mapped[] is for pure SQLAlchemy 2.x declarative_base models, not SQLModel.
"""

# ← NO "from __future__ import annotations" here — that's what broke it

import uuid as uuid_pkg
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import List, Optional

import sqlalchemy as sa
from sqlmodel import Column, Field, Relationship, SQLModel


# ════════════════════════════════════════════════════════════════════════════
# AUTH
# ════════════════════════════════════════════════════════════════════════════

class UserRole(str, Enum):
    staff  = "staff"
    viewer = "viewer"
    admin  = "admin"


class User(SQLModel, table=True):
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True, index=True, nullable=False,
    )
    email:             str           = Field(unique=True, index=True, nullable=False)
    role:              UserRole      = Field(default=UserRole.viewer, nullable=False)
    otp_secret:        Optional[str] = Field(default=None)
    last_otp_timestep: Optional[int] = Field(default=None)
    is_verified:       bool          = Field(default=False)
    created_at:        datetime      = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    sessions: List["UserSession"] = Relationship(back_populates="user")


class UserSession(SQLModel, table=True):
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True, index=True, nullable=False,
    )
    user_id:    uuid_pkg.UUID = Field(foreign_key="user.id")
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime      = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    expires_at: datetime      = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=7)
    )
    user: Optional["User"] = Relationship(back_populates="sessions")


# ════════════════════════════════════════════════════════════════════════════
# ORGANISATION
# ════════════════════════════════════════════════════════════════════════════

class Faculty(SQLModel, table=True):
    id:           uuid_pkg.UUID         = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    order:        int                   = Field(unique=True, index=True, nullable=False)
    name_bangla:  str                   = Field(unique=True, nullable=False)
    name_english: Optional[str]         = Field(default=None, unique=True)
    departments:  List["Department"]    = Relationship(back_populates="faculty")


class Department(SQLModel, table=True):
    id:            uuid_pkg.UUID              = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    name_bangla:   str                        = Field(unique=True, nullable=False)
    name_english:  Optional[str]              = Field(default=None, unique=True)
    alias_bangla:  str                        = Field(unique=True, nullable=False)
    alias_english: Optional[str]              = Field(default=None, unique=True)
    faculty_id:    uuid_pkg.UUID              = Field(foreign_key="faculty.id", index=True, nullable=False)
    faculty:       Optional["Faculty"]        = Relationship(back_populates="departments")
    participants:  List["ParticipantCard"]    = Relationship(back_populates="department")


# ════════════════════════════════════════════════════════════════════════════
# PARTICIPANTS
# ════════════════════════════════════════════════════════════════════════════

class MemberRole(str, Enum):
    DEAN    = "Dean"
    HEAD    = "Head"
    REGULAR = "Regular"


class MeetingParticipantLink(SQLModel, table=True):
    """Many-to-many join: Meeting ↔ ParticipantCard."""
    meeting_id:          uuid_pkg.UUID = Field(foreign_key="meeting.id",         primary_key=True)
    participant_card_id: uuid_pkg.UUID = Field(foreign_key="participantcard.id", primary_key=True)


class ParticipantCard(SQLModel, table=True):
    """One row per unique participant string seen in meeting minutes."""
    id:            uuid_pkg.UUID            = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    content:       str                      = Field(index=True)
    role:          MemberRole               = Field(default=MemberRole.REGULAR, index=True)
    email:         Optional[str]            = Field(default=None, nullable=True)
    department_id: uuid_pkg.UUID            = Field(foreign_key="department.id", index=True)
    department:    Optional["Department"]   = Relationship(back_populates="participants")
    meetings:      List["Meeting"]          = Relationship(
        back_populates="members",
        link_model=MeetingParticipantLink,
    )


# ════════════════════════════════════════════════════════════════════════════
# FILES  (local filesystem, S3-migration-ready)
# ════════════════════════════════════════════════════════════════════════════

class UploadedFile(SQLModel, table=True):
    """
    Metadata for every uploaded file. Binary data lives under MEDIA_ROOT.

    original_filename   User-visible name ("Annual Report.pdf").
    stored_filename     UUID-based name on disk — collision-proof.
    path                Relative path from MEDIA_ROOT.
    storage_key         Null for local storage; set to S3 key when migrating.
    mime_type           For correct Content-Type header when serving.
    size_bytes          For UI display and quota checks.
    """
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True, index=True, nullable=False,
    )
    original_filename: str           = Field(nullable=False)
    stored_filename:   str           = Field(nullable=False, unique=True)
    path:              str           = Field(nullable=False)
    storage_key:       Optional[str] = Field(default=None, nullable=True)
    mime_type:         str           = Field(nullable=False)
    size_bytes:        int           = Field(nullable=False)
    uploaded_at:       datetime      = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    agendum_annexures:      List["AgendumAnnexure"]      = Relationship(back_populates="file")
    resolution_attachments: List["ResolutionAttachment"] = Relationship(back_populates="file")


# ════════════════════════════════════════════════════════════════════════════
# MEETINGS
# ════════════════════════════════════════════════════════════════════════════

class Meeting(SQLModel, table=True):
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True, index=True, nullable=False,
    )
    serial_num:        int                     = Field(index=True, nullable=False)
    is_academic:       bool                    = Field(default=True, nullable=False)
    title:             str                     = Field(nullable=False)
    description:       Optional[str]           = Field(default=None)
    conclusion:        Optional[str]           = Field(default=None)
    is_finished:       bool                    = Field(default=False, nullable=False)
    created_at:        datetime                = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    meeting_date:      Optional[datetime]      = Field(default=None)
    president_card_id: Optional[uuid_pkg.UUID] = Field(
        default=None, foreign_key="participantcard.id"
    )

    # Cached paths to generated PDFs (relative to MEDIA_ROOT)
    agenda_pdf: Optional[uuid_pkg.UUID] = Field(default=None, foreign_key="uploadedfile.id", nullable=True)
    resolution_pdf: Optional[uuid_pkg.UUID] = Field(default=None, foreign_key="uploadedfile.id", nullable=True)

    members: List["ParticipantCard"] = Relationship(
        back_populates="meetings",
        link_model=MeetingParticipantLink,
    )
    agendas: List["Agendum"] = Relationship(back_populates="meeting")


# ════════════════════════════════════════════════════════════════════════════
# AGENDA ITEMS
# ════════════════════════════════════════════════════════════════════════════

class Agendum(SQLModel, table=True):
    """
    One agenda item (প্রস্তাব) within a Meeting.

    serial            1-based display order.
    is_supplementary  True for items added mid-meeting (অতিরিক্ত প্রস্তাব).
    body              Tiptap JSON stored as text. Cast to dict in schemas.
    updated_at        Set explicitly on every PATCH — useful for audit trail.
    """
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True, index=True, nullable=False,
    )
    serial:           int                = Field(nullable=False, index=True)
    body:             Optional[str]      = Field(default=None)
    is_supplementary: bool               = Field(default=False, nullable=False)
    created_at:       datetime           = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at:  Optional[datetime]  = Field(default=None, nullable=True)
    meeting_id:  uuid_pkg.UUID       = Field(foreign_key="meeting.id", index=True, nullable=False)

    meeting:    Optional["Meeting"]       = Relationship(back_populates="agendas")
    resolution: Optional["Resolution"]    = Relationship(back_populates="agendum")
    annexures:  List["AgendumAnnexure"]   = Relationship(back_populates="agendum")


# ════════════════════════════════════════════════════════════════════════════
# RESOLUTIONS
# ════════════════════════════════════════════════════════════════════════════

class Resolution(SQLModel, table=True):
    """
    Formal decision (সিদ্ধান্ত) arising from one Agendum.
    UNIQUE on agendum_id enforces the 1-to-1 at DB level.
    """
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True, index=True, nullable=False,
    )
    body:       Optional[str]     = Field(default=None)
    created_at: datetime          = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Optional[datetime] = Field(default=None, nullable=True)

    # sa_column used here to add the UNIQUE constraint (not possible via Field alone)
    agendum_id: uuid_pkg.UUID = Field(
        sa_column=Column(
            sa.UUID(as_uuid=True),
            sa.ForeignKey("agendum.id"),
            unique=True,
            nullable=False,
            index=True,
        )
    )

    agendum:     Optional["Agendum"]          = Relationship(back_populates="resolution")
    attachments: List["ResolutionAttachment"] = Relationship(back_populates="resolution")


# ════════════════════════════════════════════════════════════════════════════
# FILE ATTACHMENT JUNCTION TABLES
# ════════════════════════════════════════════════════════════════════════════

class AgendumAnnexure(SQLModel, table=True):
    """
    Ordered attachment of an UploadedFile to an Agendum (0-to-many).
    Unique constraint prevents the same file being attached twice.
    """
    id:         uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True, nullable=False)
    agendum_id: uuid_pkg.UUID = Field(foreign_key="agendum.id",      index=True, nullable=False)
    file_id:    uuid_pkg.UUID = Field(foreign_key="uploadedfile.id", index=True, nullable=False)
    order:      int           = Field(nullable=False, default=1)

    agendum: Optional["Agendum"]      = Relationship(back_populates="annexures")
    file:    Optional["UploadedFile"] = Relationship(back_populates="agendum_annexures")

    __table_args__ = (
        sa.UniqueConstraint("agendum_id", "file_id", name="uq_agendum_file"),
    )


class ResolutionAttachment(SQLModel, table=True):
    """Ordered attachment of an UploadedFile to a Resolution (0-to-many)."""
    id:            uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True, nullable=False)
    resolution_id: uuid_pkg.UUID = Field(foreign_key="resolution.id",   index=True, nullable=False)
    file_id:       uuid_pkg.UUID = Field(foreign_key="uploadedfile.id", index=True, nullable=False)
    order:         int           = Field(nullable=False, default=1)

    resolution: Optional["Resolution"]   = Relationship(back_populates="attachments")
    file:       Optional["UploadedFile"] = Relationship(back_populates="resolution_attachments")

    __table_args__ = (
        sa.UniqueConstraint("resolution_id", "file_id", name="uq_resolution_file"),
    )