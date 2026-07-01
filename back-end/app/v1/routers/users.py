"""User Management and Registration Router for eCouncil Engine V1.

Handles authentication profiling, administrative account provisioning, 
and directory access state lookups.
"""

from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status, Body
from pwdlib import PasswordHash
from sqlalchemy import insert, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.rbac import RoleChecker, get_current_user
from app.models import user_table, UserRole, user_session_table
from app.schemas import UserSecurePayload

from app.v1.schemas.users import (
    UserRegisterRequest, UserRegisterResponseList,
    SessionHistoryRecord
)

router = APIRouter(prefix="/users", tags=["User Management V1"])

# Initialize the lightweight password hashing utility configured with Argon2id
password_hash = PasswordHash.recommended()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserRegisterResponseList,
    dependencies=[Depends(RoleChecker([UserRole.ADMIN]))],
    summary="1. Bulk Register New Council Users",
)
async def register_users(
    payload: list[UserRegisterRequest] = Body(..., min_length=1),
    db: AsyncSession = Depends(get_db)
):
    """Administratively provisions a JSON array containing one or many new user profiles.

    ### Authorization Constraints:
    - **Restricted Access**: Exclusive to users carrying the **`admin`** structural system role.

    ### Operational Execution Parameters:
    1. Validates that the input payload contains an array with at least **one valid object**.
    2. Performs an initial duplicate safety evaluation to verify that none of the requested email addresses already exist inside the system matrix.
    3. Provisions records dynamically with individual unique UUIDs and an Argon2id hashed temporary password string format.

    ### HTTP Response Codes Matrix:
    - **201 Created**: All accounts batch processed and safely committed to the database.
    - **400 Bad Request**: Input JSON array missing or contains fewer than 1 entry.
    - **401 Unauthorized**: Session missing, malformed structural layout context, or expired.
    - **403 Forbidden**: Active identity lacks necessary administrative clearance level.
    - **409 Conflict**: One or more email addresses provided already exist in the database catalog.
    - **500 Internal Server Error**: Unhandled database write exception or connection interruption.
    """
    requested_emails = [item.email.lower() for item in payload]
    
    # Check for existing email targets
    check_query = select(user_table.c.email).where(user_table.c.email.in_(requested_emails))
    check_result = await db.execute(check_query)
    existing_emails = {row[0] for row in check_result.all()}

    if existing_emails:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Registration failed. The following email assets already exist: {list(existing_emails)}"
        )

    inserted_profiles = []

    try:
        for account in payload:
            generated_id = uuid4()
            clean_email = account.email.lower()
            
            # Generate temporary cleartext password string
            temp_raw_pass = f"Welcome_eCouncil_{clean_email.split('@')[0]}"
            
            # Compute a highly secure, salted cryptographic Argon2id string natively
            hashed_password = password_hash.hash(temp_raw_pass)

            insert_statement = insert(user_table).values(
                id=generated_id,
                email=clean_email,
                hashed_password=hashed_password,
                role=account.role.value
            )
            await db.execute(insert_statement)
            
            inserted_profiles.append({
                "id": generated_id,
                "email": clean_email,
                "role": account.role,
                "status": "provisioned_successfully"
            })

        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted due to an internal system storage exception."
        )

    return {"processed_records": inserted_profiles}

@router.get(
    "/me/sessions",
    status_code=status.HTTP_200_OK,
    response_model=list[SessionHistoryRecord],
    summary="4. Retrieve Current User Session History",
)
async def get_my_session_history(
    current_user: UserSecurePayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves a chronological ledger of all login sessions associated with the authenticated user.

    ### Authorization Constraints:
    - **Restricted Access**: Available to **any authenticated user** (Admin, Staff, or Viewer) with a valid session context.

    ### Operational Execution Parameters:
    1. Extracts the caller's unique identity profile parameters out of the incoming header.
    2. Runs an asynchronous selection query on `user_session_table` searching for rows matching the caller's `user_id`.
    3. Orders records by creation timeline string parameters (`created_at DESC`) to prioritize recent telemetry profiles.
    4. Evaluates expiration timestamps dynamically against the current time (`now`) to attach a live boolean status indicator (`is_active`).

    ### HTTP Response Codes Matrix:
    - **200 OK**: Ledger successfully extracted and mapped. Returns an array of historical sessions.
    - **401 Unauthorized**: Token profile missing, invalid, or expired.
    - **500 Internal Server Error**: Internal database connection drops or query failures.
    """
    now = datetime.now(timezone.utc)

    # Compile explicit selection query targeting user session maps
    # SELECT id, ip_address, user_agent, created_at, expires_at FROM user_session 
    # WHERE user_id = :user_id ORDER BY created_at DESC;
    query = (
        select(
            user_session_table.c.id.label("session_id"),
            user_session_table.c.ip_address,
            user_session_table.c.user_agent,
            user_session_table.c.created_at,
            user_session_table.c.expires_at
        )
        .where(user_session_table.c.user_id == current_user.id)
        .order_by(desc(user_session_table.c.created_at))
    )

    try:
        result = await db.execute(query)
        session_rows = result.mappings().all()

        history_ledger = []
        for row in session_rows:
            # Dynamically compute if a session is still valid or has expired
            is_active_session = row["expires_at"] > now

            history_ledger.append({
                "session_id": row["session_id"],
                "ip_address": row["ip_address"],
                "user_agent": row["user_agent"],
                "created_at": row["created_at"],
                "expires_at": row["expires_at"],
                "is_active": is_active_session
            })

        return history_ledger

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted: System encountered an issue querying active telemetry logs."
        )