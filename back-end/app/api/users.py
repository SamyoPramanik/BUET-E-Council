import logging

from fastapi import APIRouter, Depends, Header, HTTPException, status, Response
from sqlmodel import Session, select, desc, delete, col
from typing import Dict, Any, List
from uuid import UUID

from ..database import get_session
from ..models import User, UserSession
from ..schemas.users import UserCreate, UserRead
from ..dependencies import get_current_user, get_admin_user
from ..utils import hash_password, generate_random_password, send_credentials_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "",
    response_model=List[UserRead],
    status_code=status.HTTP_200_OK,
)
async def list_users(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_session),
):
    """Admin-only: lists all user accounts."""
    return db.exec(select(User).order_by(desc(User.created_at))).all()


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Account created and credentials emailed"},
        409: {"description": "Email already registered"},
    },
)
async def create_user(
    payload: UserCreate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_session),
):
    """
    Admin-only: creates a new account (staff/viewer/admin).

    Uses the given password, or auto-generates one if omitted, then emails
    the plaintext password to the new account's address. The plaintext
    password is never stored or returned in the API response.
    """
    existing = db.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    plain_password = payload.password or generate_random_password()

    new_user = User(
        email=payload.email,
        role=payload.role,
        hashed_password=hash_password(plain_password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    try:
        await send_credentials_email(new_user.email, plain_password)
    except Exception as email_err:
        # The account is already created; just log so the admin can notice
        # and hand the password over some other way if delivery failed.
        logger.error(f"Failed to email credentials to {new_user.email}: {email_err}")

    return new_user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: UUID,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_session),
):
    """Admin-only: removes a user account (and its sessions)."""
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account.",
        )

    target = db.get(User, user_id)
    if not target:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    db.exec(delete(UserSession).where(col(UserSession.user_id) == user_id))
    db.delete(target)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


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