import logging

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlmodel import Session, select
from uuid import UUID

from ..database import get_session
from ..models import User, UserSession
from ..schemas.auth import LoginRequest, ChangePasswordRequest
from ..utils import verify_password, hash_password
from ..dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Login successful, session created"},
        401: {"description": "Invalid email or password"},
    },
)
async def login(
    request: Request,
    credentials: LoginRequest,
    db: Session = Depends(get_session),
):
    """Authenticates a user by email + password and creates a trackable session."""
    user = db.exec(select(User).where(User.email == credentials.email)).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        logger.info(f"Failed login attempt for email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    new_session = UserSession(
        user_id=user.id,
        ip_address=request.client.host if request.client else "0.0.0.0",
        user_agent=request.headers.get("user-agent", "unknown"),
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    logger.info(f"User {user.email} logged in successfully. Session: {new_session.id}")

    return {
        "status": "success",
        "data": {
            "session_id": str(new_session.id),
            "user_role": user.role,
            "expires_at": new_session.expires_at,
        },
    }


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Password changed successfully"},
        400: {"description": "Current password is incorrect"},
    },
)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Lets a logged-in user change their own password."""
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    current_user.hashed_password = hash_password(payload.new_password)
    db.add(current_user)
    db.commit()

    return None


@router.delete(
    "/sign-out",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Successfully signed out"},
        401: {"description": "Invalid session"},
        404: {"description": "Session record not found"},
    },
)
async def sign_out(
    current_user: User = Depends(get_current_user),
    session_id: UUID = Header(...),
    db: Session = Depends(get_session),
):
    """Deletes the current session from the database."""
    statement = select(UserSession).where(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id,
    )
    session_record = db.exec(statement).first()

    if not session_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )

    db.delete(session_record)
    db.commit()

    return None
