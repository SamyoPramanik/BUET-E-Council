"""Session-Backed RBAC Guard Engine for the eCouncil System.

Authenticates user identities by verifying structural session tokens natively 
against the database and enforces granular system role permissions.
"""

from datetime import datetime, timezone
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import user_table, user_session_table, UserRole
from app.schemas import UserSecurePayload

# We'll expect the frontend to pass the session UUID in a standard custom header
# change this to APIKeyCookie if you plan to use browser cookies later
session_header = APIKeyHeader(name="X-Session-ID", auto_error=True)


async def get_current_user(
    session_id_str: str = Depends(session_header),
    db: AsyncSession = Depends(get_db)
) -> UserSecurePayload:
    """Core Authentication Guard extracting user profiles via session UUID links."""
    
    # 1. Enforce correct UUID formatting string structure from the client header
    try:
        session_uuid = UUID(session_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Malformed structural session key."
        )

    # 2. Build a high-performance JOIN query looking up active sessions
    # SELECT ... FROM user_session JOIN "user" ON user.id = user_session.user_id 
    # WHERE user_session.id = :id AND user_session.expires_at > CURRENT_TIMESTAMP LIMIT 1;
    now = datetime.now(timezone.utc)
    
    query = (
        select(
            user_table.c.id,
            user_table.c.email,
            user_table.c.role,
            user_table.c.created_at,
            user_session_table.c.id.label("session_id"),
            user_session_table.c.expires_at.label("session_expires_at"),
            user_session_table.c.ip_address,
            user_session_table.c.user_agent
        )
        .join(user_table, user_table.c.id == user_session_table.c.user_id)
        .where(
            and_(
                user_session_table.c.id == session_uuid,
                user_session_table.c.expires_at > now
            )
        )
        .limit(1)
    )

    result = await db.execute(query)
    session_row = result.mappings().first()

    if not session_row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Missing, invalid, or expired database session context."
        )

    # 3. Serialize structural row attributes straight into our Pydantic model
    return UserSecurePayload.model_validate(session_row)


class RoleChecker:
    """Authorization Guard acting as a gatekeeper for restricted endpoints."""

    def __init__(self, allowed_roles: list[UserRole]):
        """Initializes authorization rule parameters.

        Args:
            allowed_roles: A list of typed UserRole enums (e.g., [UserRole.STAFF])
        """
        self.allowed_roles = [role.value for role in allowed_roles]

    def __call__(self, current_user: UserSecurePayload = Depends(get_current_user)) -> UserSecurePayload:
        """Evaluates inbound user data parameters against permission levels."""
        
        # Super-Admin Exception Rule: Admins bypass all role restriction walls automatically
        if current_user.role == UserRole.ADMIN:
            return current_user
            
        if current_user.role.value not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access Denied: Insufficient structural role privileges to view this asset."
            )
            
        return current_user