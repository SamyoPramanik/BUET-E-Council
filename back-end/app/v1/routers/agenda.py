"""Agenda Coordination and Lifecycle Router for eCouncil Engine V1."""

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy import insert, select, and_, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.dependencies.rbac import RoleChecker
from app.models import agendum_table, meeting_table, UserRole
from app.v1.schemas.agenda import (
    AgendaCreateRequest, AgendaCreateResponse,
    AgendaDeletionResponse, AgendaUpdateRequest
)

router = APIRouter(prefix="/agenda", tags=["Agenda Management V1"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=AgendaCreateResponse,
    dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.STAFF]))],
    summary="13. Instantiate Blank Agenda Item",
)
async def create_agenda_item(
    payload: AgendaCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Instantiates a blank agenda item workspace associated with a specific meeting.

    ### Authorization Constraints:
    - **Restricted Access**: Exclusive to users carrying either the **`admin`** or **`staff`** role.

    ### Operational Execution Parameters:
    1. **Meeting Guard**: Verifies that the specified `meeting_id` actually exists in the core meeting ledger.
    2. **Serial Multi-Tenant Check**: Ensures that the `serial_num` sequence slot is not already taken *within the scope of that specific meeting*.
    3. **Structural Defaults**: Initializes the item with `is_supply` defaulting to `False`, alongside empty `content` and `resolution` objects.

    ### HTTP Response Codes Matrix:
    - **201 Created**: Agenda item successfully initialized and allocated.
    - **400 Bad Request**: Validation boundary failure (e.g., serial number < 1).
    - **401 Unauthorized**: Authentication token missing or invalid.
    - **403 Forbidden**: Active caller possesses insufficient operational roles (`viewer`).
    - **404 Not Found**: The target `meeting_id` cannot be resolved.
    - **409 Conflict**: An agenda item with this exact serial number is already registered for this meeting.
    - **500 Internal Server Error**: Unhandled backend database transaction failure.
    """
    # 1. Guard: Verify the parent meeting exists
    meeting_query = select(meeting_table.c.id).where(meeting_table.c.id == payload.meeting_id).limit(1)
    meeting_result = await db.execute(meeting_query)
    if not meeting_result.scalar():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Allocation rejected: Target meeting workspace '{payload.meeting_id}' does not exist."
        )

    # 2. Guard: Verify serial number uniqueness within the scope of this meeting
    conflict_query = select(agendum_table.c.id).where(
        and_(
            agendum_table.c.serial_no == payload.serial_num,
            agendum_table.c.meeting_id == payload.meeting_id
        )
    ).limit(1)
    
    conflict_result = await db.execute(conflict_query)
    if conflict_result.scalar():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflict: Agenda index serial number {payload.serial_num} is already allocated."
        )

    # 3. Execute entry ingestion
    try:
        insert_statement = (
            insert(agendum_table)
            .values(
                serial_no=payload.serial_num,
                content=None,
                resolution=None,
                is_supply=False,
                meeting_id=payload.meeting_id
            )
            .returning(
                agendum_table.c.id, 
                agendum_table.c.serial_no, 
                agendum_table.c.is_supply,
                agendum_table.c.content,
                agendum_table.c.resolution
            )
        )

        tx_result = await db.execute(insert_statement)
        new_row = tx_result.mappings().first()

        if not new_row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database failed to return the instantiated agenda record payload."
            )

        await db.commit()

    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted: System encountered an issue allocating the agenda item record."
        )

    return {
        "id": new_row["id"],
        "meeting_id": payload.meeting_id,
        "serial_no": new_row["serial_no"],
        "is_supply": new_row["is_supply"],
        "content": new_row["content"],
        "resolution": new_row["resolution"],
        "message": "Blank agenda item workspace successfully allocated."
    }

@router.delete(
    "/{agenda_id}",
    status_code=status.HTTP_200_OK,
    response_model=AgendaDeletionResponse,
    dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.STAFF]))],
    summary="16. Delete Specific Agenda Item by ID",
)
async def delete_agenda_item(
    agenda_id: UUID = Path(..., description="The unique UUID token of the targeted agenda item to drop."),
    db: AsyncSession = Depends(get_db)
):
    """Permanently deletes a single agenda item entry from the system repository.

    ### Authorization Constraints:
    - **Restricted Access**: Exclusive to authenticated operators carrying either the **`admin`** or **`staff`** system role.

    ### Operational Execution Parameters:
    1. **Existence Guard**: Queries the system ledger to ensure the specified `agenda_id` actually exists.
    2. Runs an atomic SQL `DELETE` query to safely strip the row from the tracking table context.

    ### HTTP Response Codes Matrix:
    - **200 OK**: Target agenda item located and dropped successfully.
    - **401 Unauthorized**: Active identity header validation token is missing or dead.
    - **403 Forbidden**: Operator lacks sufficient security role permissions.
    - **404 Not Found**: No registered agenda item matches the provided `agenda_id`.
    - **500 Internal Server Error**: Database engine timeout or unhandled transaction rollback failures.
    """
    # 1. Guard: Check if the targeted agendum row exists
    # SELECT id FROM agendum WHERE id = :agenda_id LIMIT 1;
    exists_query = select(agendum_table.c.id).where(agendum_table.c.id == agenda_id).limit(1)
    exists_result = await db.execute(exists_query)
    
    if not exists_result.scalar():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deletion rejected: Target agenda item '{agenda_id}' could not be resolved."
        )

    # 2. Execute target row data erasure block
    # DELETE FROM agendum WHERE id = :agenda_id;
    try:
        delete_statement = delete(agendum_table).where(agendum_table.c.id == agenda_id)
        await db.execute(delete_statement)
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted: System encountered an error removing the target agenda record row."
        )

    return {
        "agenda_id": agenda_id,
        "message": "Agenda item entry was successfully located and permanently dropped from the ledger database."
    }

@router.patch(
    "/{agenda_id}",
    status_code=status.HTTP_200_OK,
    response_model=AgendaCreateResponse,
    dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.STAFF]))],
    summary="17. Partially Update Agenda Item Attributes",
)
async def update_agenda_item_attributes(
    payload: AgendaUpdateRequest,
    agenda_id: UUID = Path(..., description="The unique UUID token of the target agenda item to update."),
    db: AsyncSession = Depends(get_db)
):
    """Partially modifies column attributes inside an active agenda row matrix.

    ### Authorization Constraints:
    - **Restricted Access**: Exclusive to authenticated operators carrying either the **`admin`** or **`staff`** system role.

    ### Validation Safety Matrix:
    1. **Existence Guard**: Verifies that the targeted `agenda_id` actually exists inside the ledger registry.
    2. **Field Extraction Safety**: Reads payload mapping metrics using `exclude_unset=True` to avoid overwriting unmentioned fields with defaults.

    ### HTTP Response Codes Matrix:
    - **200 OK**: Successfully updated the target database record. Returns updated metrics.
    - **400 Bad Request**: Input validation boundary constraints broken (e.g., `serial_num` < 1).
    - **401 Unauthorized**: Calling identity header verification validation token is missing or dead.
    - **403 Forbidden**: Operator holds insufficient system operational clearance rights.
    - **404 Not Found**: Target agenda record item could not be resolved.
    - **500 Internal Server Error**: Database storage connection drop or transaction write failure.
    """
    # 1. Guard: Check if the targeted agendum row exists
    exists_query = select(agendum_table.c.id).where(agendum_table.c.id == agenda_id).limit(1)
    exists_result = await db.execute(exists_query)
    
    if not exists_result.scalar():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Modification rejected: Target agenda item '{agenda_id}' could not be resolved."
        )

    # 2. Isolate fields explicitly targeted by the incoming payload block
    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Process aborted: Request body must contain at least one valid modification key attribute."
        )

    # 3. Align pydantic model schema property keys with actual backend table column targets
    if "serial_num" in update_data:
        update_data["serial_no"] = update_data.pop("serial_num")
    if "resolution_content" in update_data:
        update_data["resolution"] = update_data.pop("resolution_content")

    # 4. Construct and execute the update statement transaction block
    try:
        update_statement = (
            update(agendum_table)
            .where(agendum_table.c.id == agenda_id)
            .values(**update_data)
            .returning(
                agendum_table.c.id,
                agendum_table.c.meeting_id,
                agendum_table.c.serial_no,
                agendum_table.c.is_supply,
                agendum_table.c.content,
                agendum_table.c.resolution
            )
        )

        tx_result = await db.execute(update_statement)
        updated_row = tx_result.mappings().first()

        if not updated_row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error: Update transaction did not return the modified record row context."
            )

        await db.commit()

        return {
            "id": updated_row["id"],
            "meeting_id": updated_row["meeting_id"],
            "serial_no": updated_row["serial_no"],
            "is_supply": updated_row["is_supply"],
            "content": updated_row["content"],
            "resolution": updated_row["resolution"],
            "message": "Agenda item metadata row fields successfully updated."
        }

    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted: System encountered an issue writing updates to the target agenda row entry."
        )