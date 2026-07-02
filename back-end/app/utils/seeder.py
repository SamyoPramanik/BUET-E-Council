"""Data Seeding Utility Module for Importing Historical Meeting Documents."""

import json
from pathlib import Path
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import select, insert, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import meeting_table, member_table, meeting_member_table, agendum_table, department_table


async def parse_and_seed_meeting_json(folder_name: str, file_name: str, db: AsyncSession) -> dict:
    """Parses an eCouncil meeting JSON schema document and populates database tables.

    ### Args:
        folder_name (str): Relative or absolute directory path (e.g., "data/seeds").
        file_name (str): Core target file string matching target asset (e.g., "meeting_463.json").
        db (AsyncSession): Active transactional asynchronous database session handle.

    ### Returns:
        dict: Operational summary matrix tracking newly generated entity counts.
    """
    # 1. Resolve absolute file workspace boundaries safely
    base_path = Path(__file__).resolve().parent.parent.parent
    target_file_path = base_path / folder_name / file_name

    if not target_file_path.exists() or not target_file_path.is_file():
        raise FileNotFoundError(f"Migration aborted: Target JSON file missing at location: '{target_file_path}'")

    # 2. Parse raw character buffer data stream into dictionary
    try:
        with open(target_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as err:
        raise ValueError(f"Parsing failure: Target file format contains broken or malformed JSON tokens: {str(err)}")

    # 3. Conflict Guard: Verify this specific meeting hasn't already been imported
    serial_num = data.get("meeting_serial")
    is_academic = data.get("is_academic", True)

    meeting_check = select(meeting_table.c.id).where(
        and_(
            meeting_table.c.serial_num == serial_num,
            meeting_table.c.is_academic == is_academic
        )
    ).limit(1)
    
    check_result = await db.execute(meeting_check)
    if check_result.scalar():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Migration skipped: Meeting with Serial {serial_num} (Academic: {is_academic}) already exists."
        )

    try:
        # 4. Ingest Parent Core Meeting Row Entry
        meeting_date_str = data.get("date")
        # Parse ISO standard timestamp (e.g., "2021-04-22T14:00:00+06:00") cleanly
        parsed_date = datetime.fromisoformat(meeting_date_str) if meeting_date_str else datetime.utcnow()

        meeting_stmt = (
            insert(meeting_table)
            .values(
                title=data.get("meeting_title"),
                description=data.get("description"),
                conclusion=data.get("conclusion"),
                president=data.get("president"),
                serial_num=serial_num,
                is_academic=is_academic,
                status="draft",  # Default baseline state initial positioning
                meeting_date=parsed_date
            )
            .returning(meeting_table.c.id)
        )
        meeting_res = await db.execute(meeting_stmt)
        meeting_id = meeting_res.scalar()

        # 5. Process and Map Roster Members Loop Matrix
        members_list = data.get("members", [])
        member_mappings_count = 0

        for m_data in members_list:
            alias_to_find = m_data.get("department_alias")
            
            # Lookup corresponding department ID by alias match
            dept_query = select(department_table.c.id).where(department_table.c.alias == alias_to_find).limit(1)
            dept_res = await db.execute(dept_query)
            department_id = dept_res.scalar()

            # Attempt to find if a member with this identical structural text block content already exists
            member_find_query = select(member_table.c.id).where(member_table.c.content == m_data.get("content")).limit(1)
            member_find_res = await db.execute(member_find_query)
            member_id = member_find_res.scalar()

            # If member description profile doesn't exist, build a new structural tracking row
            if not member_id:
                new_member_stmt = (
                    insert(member_table)
                    .values(
                        content=m_data.get("content"),
                        is_academic=is_academic,
                        is_external=m_data.get("is_external", False),
                        department_id=department_id,
                        hide=True  # Initial default safety parameter block restriction boundary
                    )
                    .returning(member_table.c.id)
                )
                new_member_res = await db.execute(new_member_stmt)
                member_id = new_member_res.scalar()

            # Create entry inside the junction bridge relation table mapping (meeting_member)
            await db.execute(
                insert(meeting_member_table).values(meeting_id=meeting_id, member_id=member_id)
            )
            member_mappings_count += 1

        # 6. Process and Parse Meeting Agenda Blocks
        agenda_list = data.get("agenda", [])
        agenda_items_count = 0

        for a_data in agenda_list:
            # We wrap raw localized string fields within standard JSON arrays to align with your JSONB schema format
            structured_content = {"text": a_data.get("content")} if a_data.get("content") else None
            structured_resolution = {"text": a_data.get("resolution_contents")} if a_data.get("resolution_contents") else None

            await db.execute(
                insert(agendum_table).values(
                    serial_no=a_data.get("no"),
                    content=structured_content,
                    resolution=structured_resolution,
                    is_supply=a_data.get("is_suppli", False), # Notice fallback catch parsing your JSON key typo
                    meeting_id=meeting_id
                )
            )
            agenda_items_count += 1

        # Commit all table entries atomically within a single transaction sequence block
        await db.commit()

        return {
            "status": "success",
            "meeting_id": str(meeting_id),
            "meeting_serial": serial_num,
            "members_linked_count": member_mappings_count,
            "agenda_items_imported_count": agenda_items_count,
            "message": "Historical JSON file data successfully ingested and written to database ledger safely."
        }

    except Exception as err:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration aborted: Atomic transaction block rolled back due to error: {str(err)}"
        )