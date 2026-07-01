"""SQLAlchemy Core table metadata definitions.

This module explicitly mirrors the raw database schema structures initialized 
by init.sql, allowing type-safe async query generation with SQLAlchemy Core.
"""

import enum
from sqlalchemy import (
    MetaData, Table, Column,
    String, DateTime, Enum,
    text, ForeignKey, Boolean,
    Integer, BigInteger
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

# Shared metadata catalog that will hold all table definitions
metadata = MetaData()


# =============================================================================
# 1. ENUMS DEFINITIONS
# =============================================================================
class UserRole(str, enum.Enum):
    """Mirror of the PostgreSQL 'user_role' ENUM."""
    STAFF = "staff"
    VIEWER = "viewer"
    ADMIN = "admin"

class MeetingStatus(str, enum.Enum):
    """Mirror of the PostgreSQL 'user_role' ENUM."""
    DRAFT = 'draft'
    OPEN = 'open'
    CLOSED = 'closed'


# =============================================================================
# 2. CORE ACCESS TABLES
# =============================================================================
user_table = Table(
    "user",
    metadata,
    Column(
        "id", 
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    ),
    Column("email", String(255), nullable=False, unique=True),
    Column("hashed_password", String, nullable=False),
    Column(
        "role",
        Enum(UserRole, name="user_role", inherit_schema=True, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        server_default=text("'viewer'")
    ),
    Column(
        "created_at", 
        DateTime(timezone=True), 
        nullable=False, 
        server_default=text("CURRENT_TIMESTAMP")
    )
)

# =============================================================================
# USER SESSION TABLE
# =============================================================================
user_session_table = Table(
    "user_session",
    metadata,
    Column(
        "id", 
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    ),
    Column(
        "user_id", 
        UUID(as_uuid=True), 
        ForeignKey("user.id", ondelete="CASCADE"), 
        nullable=False
    ),
    Column("ip_address", String(45), nullable=True),
    Column("user_agent", String, nullable=True),
    Column(
        "created_at", 
        DateTime(timezone=True), 
        nullable=False, 
        server_default=text("CURRENT_TIMESTAMP")
    ),
    Column(
        "expires_at", 
        DateTime(timezone=True), 
        nullable=False, 
        server_default=text("(CURRENT_TIMESTAMP + INTERVAL '7 days')")
    )
)

# =============================================================================
# INSTITUTIONAL TABLES
# =============================================================================

# Faculty Table
faculty_table = Table(
    "faculty",
    metadata,
    Column(
        "id", 
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    ),
    Column("name_bangla", String(255), nullable=False, unique=True),
    Column("name_english", String(255), nullable=True, unique=True)
)

# Department Table
department_table = Table(
    "department",
    metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    ),
    Column("name_bangla", String(255), nullable=False, unique=True),
    Column("name_english", String(255), nullable=True, unique=True),
    Column("alias", String(50), nullable=False, unique=True, index=True),
    Column(
        "faculty_id", 
        UUID(as_uuid=True), 
        ForeignKey("faculty.id", ondelete="SET NULL"), 
        nullable=True
    )
)

# =============================================================================
# MEMBER TABLE
# =============================================================================
member_table = Table(
    "member",
    metadata,
    Column(
        "id", 
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    ),
    Column("content", String, nullable=False),  # Maps to TEXT in Postgres
    Column("email", String(255), nullable=True, unique=True, index=True),
    Column(
        "hide", 
        Boolean, 
        nullable=False, 
        server_default=text("TRUE")
    ),
    Column(
        "is_academic", 
        Boolean, 
        nullable=False, 
        server_default=text("FALSE")
    ),
    Column(
        "is_external", 
        Boolean, 
        nullable=False, 
        server_default=text("FALSE")
    ),
    Column(
        "department_id", 
        UUID(as_uuid=True), 
        ForeignKey("department.id", ondelete="SET NULL"), 
        nullable=True
    )
)

# Agendum Table
agendum_table = Table(
    "agendum",
    metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    ),
    Column("serial_no", Integer, nullable=False, index=True),
    Column("content", JSONB, nullable=True),
    Column("resolution", JSONB, nullable=True),
    Column(
        "is_supply",
        Boolean,
        nullable=False,
        server_default=text("FALSE")
    ),
    Column(
        "meeting_id",
        UUID(as_uuid=True),
        ForeignKey("meeting.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
)

# Signature Table
signature_table = Table(
    "signature",
    metadata,
    Column(
        "id", 
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    ),
    Column("content", String, nullable=False),
    Column(
        "hide", 
        Boolean, 
        nullable=False, 
        server_default=text("TRUE")
    )
)

file_table = Table(
    "file",
    metadata,
    Column(
        "id", 
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    ),
    Column("original_name", String(255), nullable=False),
    Column("storage_key", String(512), nullable=False),
    Column("mime_type", String(100), nullable=False),
    Column("file_size", BigInteger, nullable=False),
    Column(
        "created_at", 
        DateTime(timezone=True), 
        nullable=False, 
        server_default=text("CURRENT_TIMESTAMP")
    )
)

meeting_table = Table(
    "meeting",
    metadata,
    Column(
        "id", 
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    ),
    Column("title", String(255), nullable=False),
    Column("description", String, nullable=True),
    Column("conclusion", String, nullable=True),
    Column("president", String(255), nullable=True),
    Column("serial_num", Integer, nullable=False, index=True),
    Column(
        "status",
        Enum(MeetingStatus, name="meeting_status", inherit_schema=True, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        server_default=text("'draft'")
    ),
    Column(
        "is_academic", 
        Boolean, 
        nullable=False, 
        server_default=text("TRUE")
    ),
    Column(
        "created_at", 
        DateTime(timezone=True), 
        nullable=False, 
        server_default=text("CURRENT_TIMESTAMP")
    ),
    
    # Document Foreign Key Linkages
    Column(
        "agenda_file_id", 
        UUID(as_uuid=True), 
        ForeignKey("file.id", ondelete="SET NULL"), 
        nullable=True,
        index=True
    ),
    Column(
        "resolution_file_id", 
        UUID(as_uuid=True), 
        ForeignKey("file.id", ondelete="SET NULL"), 
        nullable=True,
        index=True
    ),
    Column("meeting_date", DateTime(timezone=True), nullable=False)
)

# Meeting-Signature M2M
meeting_signature_table = Table(
    "meeting_signature",
    metadata,
    Column("meeting_id", UUID(as_uuid=True), ForeignKey("meeting.id", ondelete="CASCADE"), primary_key=True),
    Column("signature_id", UUID(as_uuid=True), ForeignKey("signature.id", ondelete="CASCADE"), primary_key=True)
)

# Meeting-Member M2M
meeting_member_table = Table(
    "meeting_member",
    metadata,
    Column("meeting_id", UUID(as_uuid=True), ForeignKey("meeting.id", ondelete="CASCADE"), primary_key=True),
    Column("member_id", UUID(as_uuid=True), ForeignKey("member.id", ondelete="CASCADE"), primary_key=True)
)