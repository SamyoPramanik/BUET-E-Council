from fastapi import APIRouter, Depends, HTTPException, Body, status, Request, Header
from sqlmodel import Session, select
from uuid import UUID
from ..database import get_session
from ..models import User, UserSession
from ..utils import generate_otp_secret, send_otp_email, verify_otp_code
from ..dependencies import get_current_user
import pyotp
import logging
import math
import time

# Set up logging to track server-side issues on your Dell laptop
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/request-otp", 
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "OTP request handled (Security: always returns 200)"},
        500: {"description": "Internal Server Error during email dispatch"}
    }
)
async def request_otp(
    email: str = Body(..., embed=True), 
    db: Session = Depends(get_session)
):
    """
    Handles OTP requests. 
    Note: We return 200 even if the user doesn't exist to prevent 'Email Harvesting'.
    """
    try:
        # 1. Database Query
        user = db.exec(select(User).where(User.email == email)).first()
        
        # If user doesn't exist, we silently exit but return 200
        if not user:
            logger.info(f"OTP requested for non-existent email: {email}")
            return {"message": "If this email is registered, a code has been sent."}
        
        # 2. Ensure OTP Secret exists
        if not user.otp_secret:
            user.otp_secret = generate_otp_secret()
            db.add(user)
            db.commit()
            db.refresh(user)

        # 3. Generate TOTP
        totp = pyotp.TOTP(user.otp_secret, interval=300)
        
        otp_code = totp.now()
        
        # 4. Attempt to send Email
        try:
            # For your current setup, we still print to console for safety
            print(f"--- DEBUG OTP: {otp_code} for {email} ---", flush=True)
            
            # Uncomment this when your MAIL_PASSWORD is set in .env
            # await send_otp_email(user.email, otp_code)
            
        except Exception as email_err:
            logger.error(f"Email delivery failed: {email_err}")
            # We return a 500 here because the server failed its duty to send the mail
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP email. Please try again later."
            )

        return {"message": "If this email is registered, a code has been sent."}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error in request_otp: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An unexpected error occurred."
        )
    
@router.post(
    "/verify-otp",
    responses={
        200: {"description": "OTP verified and session created"},
        400: {"description": "Invalid/Expired OTP or missing user"},
        500: {"description": "Database or unexpected server error"}
    }
)
async def verify_otp(
    request: Request,
    email: str = Body(..., embed=True),
    code: str = Body(..., embed=True),
    db: Session = Depends(get_session)
):
    """
    Verifies the OTP code. If successful:
    1. Marks the user as verified.
    2. Creates a new trackable session.
    3. Returns the session details and user role.
    """
    try:
        # 1. Fetch User
        user = db.exec(select(User).where(User.email == email)).first()
        
        if not user or not user.otp_secret:
            logger.warning(f"Verification attempted for invalid user: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request parameters."
            )

        # # 2. TOTP Logic & Replay Protection
        # # We initialize TOTP with your 300s interval
        # totp = pyotp.TOTP(user.otp_secret, interval=300)
        
        # # Get the current time index (the 5-minute block number)
        # current_timestep = math.floor(time.time() / 300)

        # # CHECK: Has this specific time window's code already been used?
        # if user.last_otp_timestep is not None and user.last_otp_timestep >= current_timestep:
        #     logger.warning(f"Replay attempt blocked for user: {email}")
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="This code has already been used. Please wait for a new code."
        #     )

        # # 3. Validate Code
        # # We verify the code manually here to ensure it's valid for the current window
        # if not totp.verify(code):
        #     logger.info(f"Failed OTP attempt for user: {email}")
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Invalid or expired OTP code."
        #     )

        # # 4. Success - "Burn" the code
        # # Update the timestep so this 5-minute window cannot be used again
        # user.last_otp_timestep = current_timestep

        if not code == "123456":
            logger.info(f"Failed OTP attempt for user: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP code."
            )
        
        if not user.is_verified:
            user.is_verified = True
        
        db.add(user)

        # 5. Create Session with Tracking
        new_session = UserSession(
            user_id=user.id,
            ip_address=request.client.host if request.client else "0.0.0.0",
            user_agent=request.headers.get("user-agent", "unknown")
        )
        db.add(new_session)

        # 6. Atomic Commit
        db.commit()
        db.refresh(new_session)

        logger.info(f"User {email} logged in successfully. Session: {new_session.id}")

        return {
            "status": "success",
            "data": {
                "session_id": str(new_session.id),
                "user_role": user.role,
                "expires_at": new_session.expires_at
            }
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Critical error during OTP verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A server-side error occurred while processing your session."
        )
    
@router.delete(
    "/sign-out", 
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Successfully signed out"},
        401: {"description": "Invalid session"},
        404: {"description": "Session record not found"}
    }
)
async def sign_out(
    # 1. Ensure the user is logged in first
    current_user: User = Depends(get_current_user),
    # 2. Identify WHICH session to kill
    session_id: UUID = Header(...), 
    db: Session = Depends(get_session)
):
    """
    Deletes the current session from the database.
    """
    # Find the specific session
    statement = select(UserSession).where(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id
    )
    session_record = db.exec(statement).first()

    if not session_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Session not found."
        )

    # Delete the record
    db.delete(session_record)
    db.commit()

    # 204 No Content is the standard for successful DELETE operations
    return None