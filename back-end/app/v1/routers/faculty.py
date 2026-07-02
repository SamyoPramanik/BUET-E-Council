"""Faculty Directory Router for eCouncil Engine V1.

Manages the institutional faculty catalog referenced by departments.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy import insert, select, update, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from app.database import get_db
from app.dependencies.rbac import RoleChecker, get_current_user
from app.models import faculty_table, UserRole
from app.v1.schemas.faculty import (
    FacultyCreateRequest, FacultyResponse,
    FacultyUpdateRequest, FacultyListResponse
)

router = APIRouter(prefix="/faculties", tags=["Faculty Directory V1"])

FACULTY_COLUMNS = (
    faculty_table.c.id,
    faculty_table.c.name_bangla,
    faculty_table.c.name_english,
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=FacultyResponse,
    dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.STAFF]))],
    summary="16. Register New Faculty",
)
async def create_faculty(
    payload: FacultyCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Registers a new institutional faculty entry inside the directory ledger.

    ### Authorization Constraints:
    - **Restricted Access**: Exclusive to users carrying either the **`admin`** or **`staff`** role.

    ### HTTP Response Codes Matrix:
    - **201 Created**: Faculty successfully instantiated and committed.
    - **401 Unauthorized**: Authentication token missing or invalid.
    - **403 Forbidden**: Active caller carries insufficient role permissions.
    - **409 Conflict**: A faculty with the same Bangla or English name already exists.
    - **500 Internal Server Error**: Unhandled backend database layer connection failure.
    """
    conflict_query = select(faculty_table.c.id).where(
        or_(
            faculty_table.c.name_bangla == payload.name_bangla,
            faculty_table.c.name_english == payload.name_english
        )
    ).limit(1)

    if (await db.execute(conflict_query)).scalar():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict: A faculty with this Bangla or English name already exists."
        )

    try:
        insert_statement = (
            insert(faculty_table)
            .values(name_bangla=payload.name_bangla, name_english=payload.name_english)
            .returning(*FACULTY_COLUMNS)
        )
        result = await db.execute(insert_statement)
        new_row = result.mappings().first()
        await db.commit()

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted: System encountered an issue creating the faculty record."
        )

    return new_row


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=FacultyListResponse,
    dependencies=[Depends(get_current_user)],
    summary="17. List All Faculties",
)
async def get_faculties(db: AsyncSession = Depends(get_db)):
    """Retrieves the complete institutional faculty directory.

    ### Authorization Constraints:
    - **Unrestricted Access**: Accessible to **all** validated system operators (`admin`, `staff`, `viewer`).

    ### HTTP Response Codes Matrix:
    - **200 OK**: Directory successfully evaluated and returned.
    - **401 Unauthorized**: Active identity header profile is missing, malformed, or dead.
    - **500 Internal Server Error**: Internal system storage drops or query failures.
    """
    query = select(*FACULTY_COLUMNS).order_by(faculty_table.c.name_english)

    try:
        result = await db.execute(query)
        rows = result.mappings().all()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted: System encountered an issue pulling the faculty directory."
        )

    return {"total_records": len(rows), "data": rows}


@router.get(
    "/{faculty_id}",
    status_code=status.HTTP_200_OK,
    response_model=FacultyResponse,
    dependencies=[Depends(get_current_user)],
    summary="18. Get Faculty by ID",
)
async def get_faculty_by_id(
    faculty_id: UUID = Path(..., description="The unique UUID of the target faculty."),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves a single faculty record by its unique identifier.

    ### Authorization Constraints:
    - **Unrestricted Access**: Accessible to **all** validated system operators (`admin`, `staff`, `viewer`).

    ### HTTP Response Codes Matrix:
    - **200 OK**: Target item successfully located.
    - **401 Unauthorized**: Calling identity session profile is missing, unverified, or expired.
    - **404 Not Found**: No registered faculty matches the provided `faculty_id`.
    - **500 Internal Server Error**: Unhandled backend database layer connection failure.
    """
    query = select(*FACULTY_COLUMNS).where(faculty_table.c.id == faculty_id).limit(1)

    result = await db.execute(query)
    row = result.mappings().first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource lookup failed: No faculty entry matches the specified ID: '{faculty_id}'"
        )

    return row


@router.patch(
    "/{faculty_id}",
    status_code=status.HTTP_200_OK,
    response_model=FacultyResponse,
    dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.STAFF]))],
    summary="19. Partially Update Faculty Attributes",
)
async def update_faculty(
    payload: FacultyUpdateRequest,
    faculty_id: UUID = Path(..., description="The unique UUID of the target faculty to modify."),
    db: AsyncSession = Depends(get_db)
):
    """Partially modifies mutable column values inside an existing faculty entry.

    ### Authorization Constraints:
    - **Restricted Access**: Exclusive to users carrying either the **`admin`** or **`staff`** role.

    ### HTTP Response Codes Matrix:
    - **200 OK**: Successfully modified the database. Returns the updated faculty row.
    - **400 Bad Request**: Request body contained no modification keys.
    - **401 Unauthorized**: Authentication session token is invalid or missing.
    - **403 Forbidden**: Caller possesses insufficient security clearance rights.
    - **404 Not Found**: Target faculty record cannot be resolved.
    - **409 Conflict**: The requested name already belongs to another faculty.
    - **500 Internal Server Error**: Database layer update failure.
    """
    existing_query = select(faculty_table.c.id).where(faculty_table.c.id == faculty_id).limit(1)
    if not (await db.execute(existing_query)).scalar():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Modification rejected: No faculty found with matching ID: '{faculty_id}'"
        )

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Process aborted: Request body must contain at least one valid modification key attribute."
        )

    conflict_clauses = [
        getattr(faculty_table.c, field) == value
        for field, value in update_data.items()
        if field in ("name_bangla", "name_english")
    ]
    if conflict_clauses:
        conflict_query = select(faculty_table.c.id).where(
            or_(*conflict_clauses), faculty_table.c.id != faculty_id
        ).limit(1)
        if (await db.execute(conflict_query)).scalar():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Conflict: Another faculty already uses this Bangla or English name."
            )

    try:
        update_statement = (
            update(faculty_table)
            .where(faculty_table.c.id == faculty_id)
            .values(**update_data)
            .returning(*FACULTY_COLUMNS)
        )
        result = await db.execute(update_statement)
        updated_row = result.mappings().first()
        await db.commit()

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted: System encountered an issue writing updates to the faculty row entry."
        )

    return updated_row


@router.delete(
    "/{faculty_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.STAFF]))],
    summary="20. Delete Faculty",
)
async def delete_faculty(
    faculty_id: UUID = Path(..., description="The unique UUID of the target faculty to remove."),
    db: AsyncSession = Depends(get_db)
):
    """Permanently removes a faculty entry from the directory ledger.

    Linked departments retain their rows; their `faculty_id` is cleared to `NULL`
    via the underlying `ON DELETE SET NULL` foreign key constraint.

    ### Authorization Constraints:
    - **Restricted Access**: Exclusive to users carrying either the **`admin`** or **`staff`** role.

    ### HTTP Response Codes Matrix:
    - **200 OK**: Faculty successfully deleted.
    - **401 Unauthorized**: Calling identity header token is missing or invalid.
    - **403 Forbidden**: Operator possesses insufficient security clearance rights.
    - **404 Not Found**: The target faculty could not be resolved.
    - **500 Internal Server Error**: Storage connection timeout or backend transaction failures.
    """
    existing_query = select(faculty_table.c.id).where(faculty_table.c.id == faculty_id).limit(1)
    if not (await db.execute(existing_query)).scalar():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deletion aborted: Target faculty '{faculty_id}' does not exist."
        )

    try:
        await db.execute(delete(faculty_table).where(faculty_table.c.id == faculty_id))
        await db.commit()

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted: System encountered an issue deleting the faculty row entry."
        )

    return {"id": faculty_id, "message": "Faculty successfully deleted. Linked departments have had their faculty reference cleared."}
