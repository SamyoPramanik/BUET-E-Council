"""Standalone Asset & File Storage Management Router for eCouncil Engine V1."""

import hashlib
import aiofiles
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Path as PathParam
from fastapi.responses import FileResponse
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.config import UPLOAD_DIR
from app.dependencies.rbac import RoleChecker, get_current_user
from app.models import file_table, UserRole
from app.v1.schemas.files import FileUploadResponse

router = APIRouter(prefix="/files", tags=["Asset Storage Management V1"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=FileUploadResponse,
    dependencies=[Depends(RoleChecker([UserRole.ADMIN, UserRole.STAFF]))],
    summary="18. Upload System Asset File",
)
async def upload_system_file(
    file: UploadFile = File(..., description="The raw binary stream multi-part file layout payload."),
    db: AsyncSession = Depends(get_db)
):
    """Ingests a multipart document stream, saving the asset safely to disk storage.

    ### Authorization Constraints:
    - **Restricted Access**: Exclusive to authenticated operators carrying either the **`admin`** or **`staff`** role.

    ### Operational Execution Parameters:
    1. **Streaming Hash Generation**: Computes a SHA-256 fingerprint hash based on the file content to establish content identity.
    2. **Unique Physical File Allocation**: Saves the target file onto disk named strictly after its hash string to protect against duplicate resource inflation.
    3. **Metadata Index Entry Ingestion**: Inserts tracking parameters (`original_filename`, `mime_type`, `file_size_bytes`) into the database.

    ### HTTP Response Codes Matrix:
    - **201 Created**: Asset successfully streamed, recorded on disk, and indexed in database.
    - **400 Bad Request**: Upload structural validation failed (e.g., zero-byte file).
    - **401 Unauthorized**: Authentication validation credentials missing or invalid.
    - **403 Forbidden**: Operator holds insufficient clearance authority.
    - **500 Internal Server Error**: Host file system write lock error or database transaction crash.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Process aborted: Uploaded file structure lacks a valid filename property entry."
        )

    try:
        # 1. Read binary content into memory to evaluate hash footprint metrics
        # Note: For massive files (>50MB), chunking loops are preferred.
        contents = await file.read()
        file_size = len(contents)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Process aborted: Cannot index or parse an empty, zero-byte document."
            )

        # Generate a unique filename using SHA-256 hash
        file_hash = hashlib.sha256(contents).hexdigest()
        file_extension = Path(file.filename).suffix
        unique_storage_name = f"{file_hash}{file_extension}"
        
        # Absolute runtime safe file path mapping derivation
        target_storage_path = UPLOAD_DIR / unique_storage_name

        # 2. Asynchronously stream and write the binary layout block to disk storage
        async with aiofiles.open(target_storage_path, "wb") as out_file:
            await out_file.write(contents)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File system write error: System failed to stream the asset block to host disk."
        )
    finally:
        await file.close()

    # 3. Commit asset profile tracking values down to the database layer
    try:
        insert_statement = (
            insert(file_table)
            .values(
                original_filename=file.filename,
                storage_path=str(target_storage_path),
                mime_type=file.content_type or "application/octet-stream",
                file_size_bytes=file_size
            )
            .returning(file_table.c.id, file_table.c.created_at)
        )

        tx_result = await db.execute(insert_statement)
        new_row = tx_result.mappings().first()

        if not new_row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error: Ingestion tracking script did not return record parameters."
            )

        await db.commit()

        return {
            "id": new_row["id"],
            "original_filename": file.filename,
            "mime_type": file.content_type or "application/octet-stream",
            "file_size_bytes": file_size,
            "created_at": new_row["created_at"],
            "message": "Document file successfully uploaded and securely indexed inside the asset matrix registry."
        }

    except Exception as e:
        await db.rollback()
        # Cleanup stranded orphaned disk assets if DB indexing fails
        if target_storage_path.exists():
            target_storage_path.unlink()
            
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted: System failed to commit asset index metadata to database ledger."
        )
    
@router.get(
    "/{file_id}",
    response_class=FileResponse,
    dependencies=[Depends(get_current_user)],  # Accessible to any authenticated role
    summary="19. Stream Asset File Binary for View/Download",
)
async def get_file_by_id(
    file_id: UUID = PathParam(..., description="The unique UUID token of the target document file asset."),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves metadata for an indexed file and streams its raw binary payload back to the client.

    ### Authorization Constraints:
    - **Unrestricted Access**: Accessible across **all** validated system operational profiles (`admin`, `staff`, `viewer`).

    ### Operational Execution Parameters:
    1. **Metadata Lookup**: Queries the registry table to obtain the absolute storage path, original name, and mime type.
    2. **Physical File Guard**: Verifies that the file actually exists on the host disk system before initiating the stream.
    3. **Binary Stream Response**: Dispatches a `FileResponse` configured with the original filename, enabling clean browser interaction.

    ### HTTP Response Codes Matrix:
    - **200 OK**: Target asset successfully located. Binary data stream is processed and returned.
    - **401 Unauthorized**: Authentication validation token header is missing, dead, or corrupted.
    - **404 Not Found**: The target `file_id` doesn't exist in the DB, or the physical file was dropped from the server disk.
    - **500 Internal Server Error**: Host system file read lock error or database communication timeout.
    """
    # 1. Fetch the file registration details from the tracking directory
    # SELECT original_filename, storage_path, mime_type FROM file WHERE id = :file_id LIMIT 1;
    query = select(
        file_table.c.original_filename,
        file_table.c.storage_path,
        file_table.c.mime_type
    ).where(file_table.c.id == file_id).limit(1)

    try:
        result = await db.execute(query)
        file_metadata = result.mappings().first()

        # DB Record Existence Guard
        if not file_metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource lookup failed: No file record matches the specified token: '{file_id}'"
            )

        # 2. Convert string to a clean Path object and verify physical existence on disk
        physical_file_path = Path(file_metadata["storage_path"])
        
        if not physical_file_path.exists() or not physical_file_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Storage conflict: The asset index exists, but the physical document is missing from the server host disk."
            )

        # 3. Compile and return the streaming file response
        # Using media_type ensures the browser knows what kind of document it is receiving.
        # filename instructs the browser what to name the file when a user triggers a download action.
        return FileResponse(
            path=physical_file_path,
            media_type=file_metadata["mime_type"],
            filename=file_metadata["original_filename"]
        )

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction aborted: System encountered an issue preparing the file download stream."
        )
    