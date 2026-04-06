from fastapi import APIRouter, Depends, Header, status, Response
from sqlmodel import Session, select, desc, delete, col
from typing import Dict, Any
from uuid import UUID

from ..database import get_session
from ..models import User, UserSession
from ..dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "/me", 
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK
)
async def read_user_me(
    # 1. Reuse our dependency to get the user object
    current_user: User = Depends(get_current_user),
    # 2. Grab the session-id from header again to identify 'this' device
    session_id: UUID = Header(...), 
    db: Session = Depends(get_session)
):
    """
    Returns the current user's profile and a list of all active sessions.
    """
    # 3. Fetch all sessions for this user
    # We sort by created_at so the newest appears first in your frontend table
    statement = (
        select(UserSession)
        .where(UserSession.user_id == current_user.id)
        .order_by(desc(UserSession.created_at)) 
    )
    
    all_sessions = db.exec(statement).all()

    # 4. Format the session list for the frontend table
    session_list = []
    for s in all_sessions:
        session_list.append({
            "id": s.id,
            "ip_address": s.ip_address,
            "user_agent": s.user_agent,
            "created_at": s.created_at,
            "expires_at": s.expires_at,
            "is_current": s.id == session_id # Boolean flag for the UI
        })

    return {
        "user_info": {
            "email": current_user.email,
            "role": current_user.role
        },
        "sessions": session_list
    }

@router.delete(
    "/sessions/{target_session_id}", 
    status_code=status.HTTP_204_NO_CONTENT
)
async def revoke_session(
    target_session_id: UUID,
    current_user: User = Depends(get_current_user),
    # We use Header to check if they are revoking 'themselves'
    current_session_id: UUID = Header(..., alias="Session-ID"), 
    db: Session = Depends(get_session)
):
    """
    Remotely revokes a session. Handles idempotency and self-revocation.
    """
    # 1. Fetch the target session
    statement = select(UserSession).where(
        UserSession.id == target_session_id,
        UserSession.user_id == current_user.id
    )
    target = db.exec(statement).first()
    
    # 2. Case: Session doesn't exist or already deleted
    # We return 204 (No Content) anyway to maintain 'Idempotency'
    # This prevents the frontend from showing an error for a success state.
    if not target:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # 3. Case: Self-Revocation
    # If the user is revoking the session they are currently using,
    # we might want to log a specific message or handle a redirect hint.
    is_self = (target_session_id == current_session_id)

    # 4. Perform Delete
    db.delete(target)
    db.commit()

    # 5. Optional: Logic for 'Self-Revocation'
    # The frontend will receive a 204. If the UI knows it just deleted
    # its own session, it should clear cookies and redirect to /login.
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete(
    "/sessions", 
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "All sessions revoked successfully"},
        401: {"description": "Authentication failed"}
    }
)
async def revoke_all_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Deletes EVERY session associated with the current user.
    """
    # 1. Create a bulk delete statement
    # This is more efficient than fetching all and looping
    statement = delete(UserSession).where(col(UserSession.user_id) == current_user.id)
    
    # 2. Execute the bulk delete
    db.exec(statement)
    db.commit()

    # 3. Standard success response for DELETE
    return Response(status_code=status.HTTP_204_NO_CONTENT)