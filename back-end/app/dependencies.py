from datetime import datetime, timezone
from uuid import UUID
from fastapi import Depends, HTTPException, status, Header
from sqlmodel import Session, select
from .database import get_session
from .models import User, UserSession

async def get_current_user(
    # We expect the frontend to send 'Session-ID' in the headers
    session_id: UUID = Header(..., alias="Session-ID"), 
    db: Session = Depends(get_session)
) -> User:
    """
    The security guard: Validates the session and returns the User object.
    """
    # 1. Look up the session in the DB
    statement = select(UserSession).where(UserSession.id == session_id)
    session_record = db.exec(statement).first()

    # 401 Unauthorized: Session doesn't exist
    if not session_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Check Expiration
    # Ensure current time is compared with the UTC expiry time
    expires_at_aware = session_record.expires_at.replace(tzinfo=timezone.utc)

    if expires_at_aware < datetime.now(timezone.utc):
        # Optional: Delete expired sessions from DB here
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again.",
        )

    # 3. Retrieve the User associated with this session
    user = db.get(User, session_record.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    return user

async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    The Admin Guard: Layers on top of get_current_user to check for 'admin' role.
    """
    # 403 Forbidden: We know who they are, but they aren't allowed here.
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Administrator privileges required."
        )
    
    return current_user