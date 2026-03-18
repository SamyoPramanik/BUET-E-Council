from enum import Enum
import uuid as uuid_pkg
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, Relationship, Column, JSON

class UserRole(str, Enum):
    staff = "staff"
    viewer = "viewer"
    admin = "admin"

class User(SQLModel, table=True):
    # UUID as the primary key
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    email: str = Field(unique=True, index=True, nullable=False)
    role: UserRole = Field(default=UserRole.viewer, nullable=False)
    otp_secret: Optional[str] = Field(default=None) # The secret used to generate codes
    last_otp_timestep: Optional[int] = Field(default=None)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Link to their sessions
    sessions: List["UserSession"] = Relationship(back_populates="user")

class UserSession(SQLModel, table=True):
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    user_id: uuid_pkg.UUID = Field(foreign_key="user.id")
    
    # Metadata for security tracking
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Expiration logic
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=7)
    )

    # Link back to user
    user: Optional[User] = Relationship(back_populates="sessions")

class Meeting(SQLModel, table=True):
    # UUID Primary Key
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    
    # Required Fields
    serial_num: int = Field(index=True, nullable=False)
    is_academic: bool = Field(default=True, nullable=False) # Academic vs Syndicate
    
    # Formatted Content - Stored as JSON objects from the editor
    # We use sa_column=Column(JSON) to ensure the DB treats it as a JSONB/JSON type
    title: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    description: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    conclusion: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    # Status
    is_finished: bool = Field(default=False, nullable=False)
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    meeting_date: Optional[datetime] = Field(default=None)

    # Relationships (Placeholder for future progress)
    # agendas: List["Agenda"] = Relationship(back_populates="meeting")