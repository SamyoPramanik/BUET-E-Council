"""Authentication State and Session Lifecycle Router for eCouncil Engine V1.

Manages dynamic session generation, credential validation, and active lease tracking.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Request, status, Path
from pwdlib import PasswordHash
from sqlalchemy import insert, select, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import user_table, user_session_table
from app.dependencies.rbac import get_current_user
from app.schemas import UserSecurePayload
from app.v1.schemas.auth import (
    LoginRequest, LoginResponse,
    LogoutResponse, SessionRevocationResponse,
    BulkSessionRevocationResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication V1"])

# Use the matching modern Argon2id validation wrapper instance
password_hash = PasswordHash.recommended()


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
    summary="2. Authenticate User and Establish Session",
)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Authenticates user credentials against the system security matrix to spawn a unique database session.

    ### Authorization Constraints:
    - **Unrestricted Access**: Publicly accessible across **all** roles (`admin`, `staff`, `viewer`).

    ### Operational Execution Parameters:
    1. Looks up the explicit profile matching the normalized inbound email key.
    2. Runs an asynchronous cryptographic match validation check against the stored password hash.
    3. Extracts host transaction details (`client-ip` and `User-Agent`) straight from the request frame headers.
    4. Records a fresh session tracking token block configured to expire in 7 days.

    ### HTTP Response Codes Matrix:
    - **200 OK**: Credentials successfully validated. Active session mapping generated and returned.
    - **401 Unauthorized**: Handled safety failure; invalid email address matching or password verification failed.
    - **422 Unprocessable Entity**: Input structure violations (e.g. malformed email syntax formats).
    - **500 Internal Server Error**: Database layer storage drops or unhandled connection timeouts.
    """
    clean_email = payload.email.lower()

    # 1. Look up user by email string
    # SELECT id, hashed_password, role FROM "user" WHERE email = :clean_email LIMIT 1;
    query = select(
        user_table.c.id, 
        user_table.c.hashed_password, 
        user_table.c.role
    ).where(user_table.c.email == clean_email).limit(1)
    
    result = await db.execute(query)
    user = result.mappings().first()

    # Security Guard: Generic message prevents account enumeration attacks
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Invalid email matching credentials or password profile."
        )

    # 2. Verify password hash securely
    is_valid = password_hash.verify(payload.password, user["hashed_password"])
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Invalid email matching credentials or password profile."
        )

    # 3. Extract request telemetry environment parameters
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    # 4. Formulate session boundary configurations
    generated_session_id = uuid4()
    now = datetime.now(timezone.utc)
    expiration_time = now + timedelta(days=7)

    try:
        # Insert configuration straight into your session table layout matrix
        insert_statement = insert(user_session_table).values(
            id=generated_session_id,
            user_id=user["id"],
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=now,
            expires_at=expiration_time
        )
        await db.execute(insert_statement)
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted: System encountered an issue compiling session metrics."
        )

    return {
        "session_id": generated_session_id,
        "role": user["role"],
        "expires_at": expiration_time,
        "message": "Session established. Supply this 'session_id' as the 'X-Session-ID' header parameter."
    }

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    response_model=LogoutResponse,
    summary="3. Terminate Session and Logout",
)
async def logout(
    current_user: UserSecurePayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Invalidates the active user session context, forcing an immediate system logout.

    ### Authorization Constraints:
    - **Restricted Access**: Available to **any authenticated user** (Admin, Staff, or Viewer) with a valid session context.

    ### Operational Execution Parameters:
    1. Extracts the running session context parsing tokens directly out of the `X-Session-ID` header.
    2. Executes an immediate target deletion query on `user_session_table` matching the active `session_id`.
    3. Revokes all active pipeline privileges instantly system-wide.

    ### HTTP Response Codes Matrix:
    - **200 OK**: Session database record wiped successfully. Access revoked.
    - **401 Unauthorized**: Session context header missing, malformed, or already expired/invalidated.
    - **500 Internal Server Error**: Database write exception or connectivity interruption.
    """
    try:
        # Perform an atomic target row deletion based on the active session ID attached to the caller
        # DELETE FROM user_session WHERE id = :session_id;
        statement = delete(user_session_table).where(
            user_session_table.c.id == current_user.session_id
        )
        
        await db.execute(statement)
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted: System encountered an issue purging session states."
        )

    return {
        "message": "Session successfully invalidated. Subsequent network requests using this token will be denied.",
        "terminated_session_id": current_user.session_id
    }

@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_200_OK,
    response_model=SessionRevocationResponse,
    summary="5. Revoke Targeted User Session",
)
async def revoke_session(
    session_id: UUID = Path(..., description="The unique UUID string of the session target to terminate."),
    current_user: UserSecurePayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Terminates a specific targeted user session row safely from the database.

    ### Authorization Constraints:
    - **Restricted Access**: Available to **any authenticated user** carrying a valid session context.

    ### Validation Safety Checks Matrix:
    1. **Self-Termination Check**: Compares `session_id` against the caller's active token. If they match, a `400 Bad Request` is raised to prevent accidental self-disconnection.
    2. **Existence Check**: Queries `user_session_table` to check if the record exists. If not found, a `404 Not Found` is thrown.
    3. **Ownership Verification**: Asserts that the targeted `user_id` matches the caller's verified `id`. If mismatched, a `403 Forbidden` error is generated immediately.

    ### HTTP Response Codes Matrix:
    - **200 OK**: Targeted session successfully found and deleted.
    - **400 Bad Request**: Attempted to revoke the current active session.
    - **401 Unauthorized**: Calling identity token is missing or expired.
    - **403 Forbidden**: Targeted session belongs to a different account entity.
    - **404 Not Found**: Targeted session ID does not exist in the active matrix ledger.
    - **500 Internal Server Error**: Storage connection timeout or unhandled execution exceptions.
    """
    # Guard 1: Prevent the user from killing their current active session connection
    if session_id == current_user.session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Operation rejected: Cannot revoke your current active session via this endpoint. "
                "Utilize the explicit POST /auth/logout endpoint instead."
            )
        )

    # Guard 2 & 3: Look up target session to verify existence and check ownership constraints
    # SELECT user_id FROM user_session WHERE id = :session_id LIMIT 1;
    exist_query = select(user_session_table.c.user_id).where(user_session_table.c.id == session_id).limit(1)
    exist_result = await db.execute(exist_query)
    target_session = exist_result.mappings().first()

    if not target_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Revocation failed: The specified session target does not exist."
        )

    if target_session["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You do not possess structural ownership privileges over this session asset."
        )

    # All validations cleared; execute atomic deletion query
    try:
        # DELETE FROM user_session WHERE id = :session_id;
        delete_statement = delete(user_session_table).where(user_session_table.c.id == session_id)
        await db.execute(delete_statement)
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted: System encountered an issue purging target data records."
        )

    return {
        "message": "Targeted device session successfully revoked and invalidated.",
        "revoked_session_id": session_id
    }

@router.delete(
    "/sessions",
    status_code=status.HTTP_200_OK,
    response_model=BulkSessionRevocationResponse,
    summary="6. Revoke All Other User Sessions",
)
async def revoke_all_other_sessions(
    current_user: UserSecurePayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Purges all historical and active sessions associated with the user, except the current active connection.

    ### Authorization Constraints:
    - **Restricted Access**: Available to **any authenticated user** (Admin, Staff, or Viewer) carrying a valid active session.

    ### Operational Execution Parameters:
    1. Extracts the caller's identity and active connection context directly from the validation header.
    2. Runs an asynchronous database match count to check if there are any other sessions to delete.
    3. Executes a targeted SQL `DELETE` statement filtering for rows where `user_id == user.id` AND `id != current_session_id`.
    4. Leaves the current active session completely intact to avoid interrupting the user's current connection.

    ### HTTP Response Codes Matrix:
    - **200 OK**: Bulk purge transaction executed successfully. Returns the total count of cleared rows.
    - **401 Unauthorized**: Session token profile is missing, malformed, or has expired.
    - **500 Internal Server Error**: Database write exception or connection interruption.
    """
    # 1. Pre-flight check: Count how many alternative sessions exist for this user
    # SELECT count(id) FROM user_session WHERE user_id = :uid AND id != :current_sid;
    count_query = select(func.count(user_session_table.c.id)).where(
        and_(
            user_session_table.c.user_id == current_user.id,
            user_session_table.c.id != current_user.session_id
        )
    )
    
    try:
        count_result = await db.execute(count_query)
        other_sessions_count = count_result.scalar() or 0

        if other_sessions_count == 0:
            return {
                "message": "No other active sessions found. Your current device connection is the only active lease.",
                "revoked_sessions_count": 0
            }

        # 2. Execute bulk target deletion query
        # DELETE FROM user_session WHERE user_id = :uid AND id != :current_sid;
        delete_statement = delete(user_session_table).where(
            and_(
                user_session_table.c.user_id == current_user.id,
                user_session_table.c.id != current_user.session_id
            )
        )
        
        await db.execute(delete_statement)
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted: System encountered an issue purging bulk session records."
        )

    return {
        "message": f"Successfully revoked and cleared {other_sessions_count} other active device sessions globally.",
        "revoked_sessions_count": other_sessions_count
    }