"""Department Directory Router for eCouncil Engine V1.

Manages the institutional department catalog nested under faculties.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy import insert, select, update, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from app.database import get_db
from app.dependencies.rbac import RoleChecker, get_current_user
from app.models import department_table, faculty_table, UserRole
from app.v1.schemas.department import (
    DepartmentCreateRequest, DepartmentResponse,
    DepartmentUpdateRequest, DepartmentListResponse
)

router = APIRouter(prefix="/departments", tags=["Department Directory V1"])

DEPARTMENT_COLUMNS = (
    department_table.c.id,
    department_table.c.name_bangla,
    department_table.c.name_english,
    department_table.c.alias,
    department_table.c.faculty_id,
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DepartmentResponse,
    dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.STAFF]))],
    summary="21. Register New Department",
)
async def create_department(
    payload: DepartmentCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Registers a new institutional department entry inside the directory ledger.

    ### Authorization Constraints:
    - **Restricted Access**: Exclusive to users carrying either the **`admin`** or **`staff`** role.

    ### HTTP Response Codes Matrix:
    - **201 Created**: Department successfully instantiated and committed.
    - **401 Unauthorized**: Authentication token missing or invalid.
    - **403 Forbidden**: Active caller carries insufficient role permissions.
    - **404 Not Found**: The provided `faculty_id` does not exist.
    - **409 Conflict**: A department with the same name or alias already exists.
    - **500 Internal Server Error**: Unhandled backend database layer connection failure.
    """
    if payload.faculty_id is not None:
        faculty_check = select(faculty_table.c.id).where(faculty_table.c.id == payload.faculty_id).limit(1)
        if not (await db.execute(faculty_check)).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Creation rejected: No faculty found with matching ID: '{payload.faculty_id}'"
            )

    conflict_query = select(department_table.c.id).where(
        or_(
            department_table.c.name_bangla == payload.name_bangla,
            department_table.c.name_english == payload.name_english,
            department_table.c.alias == payload.alias
        )
    ).limit(1)

    if (await db.execute(conflict_query)).scalar():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict: A department with this name or alias already exists."
        )

    try:
        insert_statement = (
            insert(department_table)
            .values(
                name_bangla=payload.name_bangla,
                name_english=payload.name_english,
                alias=payload.alias,
                faculty_id=payload.faculty_id
            )
            .returning(*DEPARTMENT_COLUMNS)
        )
        result = await db.execute(insert_statement)
        new_row = result.mappings().first()
        await db.commit()

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted: System encountered an issue creating the department record."
        )

    return new_row


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=DepartmentListResponse,
    dependencies=[Depends(get_current_user)],
    summary="22. List Departments",
)
async def get_departments(
    faculty_id: UUID | None = Query(None, description="Optional filter to only return departments under a specific faculty."),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves the institutional department directory, optionally scoped to a single faculty.

    ### Authorization Constraints:
    - **Unrestricted Access**: Accessible to **all** validated system operators (`admin`, `staff`, `viewer`).

    ### HTTP Response Codes Matrix:
    - **200 OK**: Directory successfully evaluated and returned.
    - **401 Unauthorized**: Active identity header profile is missing, malformed, or dead.
    - **500 Internal Server Error**: Internal system storage drops or query failures.
    """
    query = select(*DEPARTMENT_COLUMNS).order_by(department_table.c.name_english)
    if faculty_id is not None:
        query = query.where(department_table.c.faculty_id == faculty_id)

    try:
        result = await db.execute(query)
        rows = result.mappings().all()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted: System encountered an issue pulling the department directory."
        )

    return {"total_records": len(rows), "data": rows}


@router.get(
    "/{department_id}",
    status_code=status.HTTP_200_OK,
    response_model=DepartmentResponse,
    dependencies=[Depends(get_current_user)],
    summary="23. Get Department by ID",
)
async def get_department_by_id(
    department_id: UUID = Path(..., description="The unique UUID of the target department."),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves a single department record by its unique identifier.

    ### Authorization Constraints:
    - **Unrestricted Access**: Accessible to **all** validated system operators (`admin`, `staff`, `viewer`).

    ### HTTP Response Codes Matrix:
    - **200 OK**: Target item successfully located.
    - **401 Unauthorized**: Calling identity session profile is missing, unverified, or expired.
    - **404 Not Found**: No registered department matches the provided `department_id`.
    - **500 Internal Server Error**: Unhandled backend database layer connection failure.
    """
    query = select(*DEPARTMENT_COLUMNS).where(department_table.c.id == department_id).limit(1)

    result = await db.execute(query)
    row = result.mappings().first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource lookup failed: No department entry matches the specified ID: '{department_id}'"
        )

    return row


@router.patch(
    "/{department_id}",
    status_code=status.HTTP_200_OK,
    response_model=DepartmentResponse,
    dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.STAFF]))],
    summary="24. Partially Update Department Attributes",
)
async def update_department(
    payload: DepartmentUpdateRequest,
    department_id: UUID = Path(..., description="The unique UUID of the target department to modify."),
    db: AsyncSession = Depends(get_db)
):
    """Partially modifies mutable column values inside an existing department entry.

    ### Authorization Constraints:
    - **Restricted Access**: Exclusive to users carrying either the **`admin`** or **`staff`** role.

    ### HTTP Response Codes Matrix:
    - **200 OK**: Successfully modified the database. Returns the updated department row.
    - **400 Bad Request**: Request body contained no modification keys.
    - **401 Unauthorized**: Authentication session token is invalid or missing.
    - **403 Forbidden**: Caller possesses insufficient security clearance rights.
    - **404 Not Found**: Target department, or the provided `faculty_id`, cannot be resolved.
    - **409 Conflict**: The requested name or alias already belongs to another department.
    - **500 Internal Server Error**: Database layer update failure.
    """
    existing_query = select(department_table.c.id).where(department_table.c.id == department_id).limit(1)
    if not (await db.execute(existing_query)).scalar():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Modification rejected: No department found with matching ID: '{department_id}'"
        )

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Process aborted: Request body must contain at least one valid modification key attribute."
        )

    if update_data.get("faculty_id") is not None:
        faculty_check = select(faculty_table.c.id).where(faculty_table.c.id == update_data["faculty_id"]).limit(1)
        if not (await db.execute(faculty_check)).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Modification rejected: No faculty found with matching ID: '{update_data['faculty_id']}'"
            )

    conflict_clauses = [
        getattr(department_table.c, field) == value
        for field, value in update_data.items()
        if field in ("name_bangla", "name_english", "alias")
    ]
    if conflict_clauses:
        conflict_query = select(department_table.c.id).where(
            or_(*conflict_clauses), department_table.c.id != department_id
        ).limit(1)
        if (await db.execute(conflict_query)).scalar():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Conflict: Another department already uses this name or alias."
            )

    try:
        update_statement = (
            update(department_table)
            .where(department_table.c.id == department_id)
            .values(**update_data)
            .returning(*DEPARTMENT_COLUMNS)
        )
        result = await db.execute(update_statement)
        updated_row = result.mappings().first()
        await db.commit()

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted: System encountered an issue writing updates to the department row entry."
        )

    return updated_row


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.STAFF]))],
    summary="25. Delete Department",
)
async def delete_department(
    department_id: UUID = Path(..., description="The unique UUID of the target department to remove."),
    db: AsyncSession = Depends(get_db)
):
    """Permanently removes a department entry from the directory ledger.

    Linked members retain their rows; their `department_id` is cleared to `NULL`
    via the underlying `ON DELETE SET NULL` foreign key constraint.

    ### Authorization Constraints:
    - **Restricted Access**: Exclusive to users carrying either the **`admin`** or **`staff`** role.

    ### HTTP Response Codes Matrix:
    - **200 OK**: Department successfully deleted.
    - **401 Unauthorized**: Calling identity header token is missing or invalid.
    - **403 Forbidden**: Operator possesses insufficient security clearance rights.
    - **404 Not Found**: The target department could not be resolved.
    - **500 Internal Server Error**: Storage connection timeout or backend transaction failures.
    """
    existing_query = select(department_table.c.id).where(department_table.c.id == department_id).limit(1)
    if not (await db.execute(existing_query)).scalar():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deletion aborted: Target department '{department_id}' does not exist."
        )

    try:
        await db.execute(delete(department_table).where(department_table.c.id == department_id))
        await db.commit()

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted: System encountered an issue deleting the department row entry."
        )

    return {"id": department_id, "message": "Department successfully deleted. Linked members have had their department reference cleared."}
