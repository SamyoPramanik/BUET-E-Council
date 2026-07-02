"""
scripts/import_meeting_json.py
===============================
Import a single meeting (title, agenda, resolutions, members) straight from
a JSON file extracted from meeting-minutes PDFs, without hand-writing a
Python seed module for it.

Expected JSON shape — see scripts/data/meetings/a_463.json for a real example:

    {
      "meeting_serial": 463,
      "meeting_title": "...",
      "description": "...",
      "conclusion": "...",
      "president": "<free-text name/title>",
      "date": "2021-04-22T14:00:00+06:00",
      "is_academic": true,
      "members": [
        {"content": "...", "department_alias": "কেমিকৌশল", "is_external": false}
      ],
      "agenda": [
        {"no": 1, "content": "...", "resolution_contents": "...", "is_suppli": false}
      ]
    }

`department_alias` is matched against department.alias_bangla. Any member
whose `content` string isn't already a ParticipantCard in the DB is
auto-created (filed under the matched department, or "Default" if the
alias is missing/unknown) — mirroring the fallback used by the legacy
Python meeting seeds in scripts/seeds/meetings/.

Usage (run from back-end/, same convention as scripts/run_seed.py):

    PYTHONPATH=. uv run python scripts/import_meeting_json.py \\
        scripts/data/meetings/a_463.json

    # Preview only — validates + reports, rolls back instead of committing
    PYTHONPATH=. uv run python scripts/import_meeting_json.py \\
        scripts/data/meetings/a_463.json --dry-run
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlmodel import Session, select

from app.database import engine, init_db
from app.models import Agendum, Department, Meeting, MemberRole, ParticipantCard, Resolution


# ════════════════════════════════════════════════════════════════════════════
# Plain text → minimal Tiptap JSON doc (agendum.body / resolution.body are
# stored as Tiptap JSON strings — see app/api/agendas.py's `_doc` helper).
# ════════════════════════════════════════════════════════════════════════════

def _doc_from_plain_text(body: str) -> str:
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()] or [""]
    doc = {
        "type": "doc",
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": p}]}
            for p in paragraphs
        ],
    }
    return json.dumps(doc, ensure_ascii=False)


def _get_or_create_participant(
    session: Session,
    content: str,
    department_alias: Optional[str],
    is_external: bool,
    default_dept_id,
    report: list[str],
) -> ParticipantCard:
    content = content.strip()
    existing = session.exec(
        select(ParticipantCard).where(ParticipantCard.content == content)
    ).first()
    if existing:
        return existing

    dept_id = default_dept_id
    if department_alias:
        dept = session.exec(
            select(Department).where(Department.alias_bangla == department_alias)
        ).first()
        if dept:
            dept_id = dept.id
        else:
            report.append(
                f"  ! unknown department_alias '{department_alias}' for "
                f"'{content[:40]}...' — filed under Default"
            )

    card = ParticipantCard(
        content=content,
        role=MemberRole.REGULAR,
        email=None,
        department_id=dept_id,
        is_external=is_external,
    )
    session.add(card)
    session.flush()  # assigns an id without committing the transaction
    report.append(f"  + created participant card: {content[:60]}")
    return card


def import_meeting(session: Session, data: dict, report: list[str]) -> Meeting:
    conflict = session.exec(
        select(Meeting).where(
            Meeting.serial_num == data["meeting_serial"],
            Meeting.is_academic == data["is_academic"],
        )
    ).first()
    if conflict:
        council = "Academic Council" if data["is_academic"] else "Syndicate"
        raise ValueError(f"Meeting #{data['meeting_serial']} ({council}) already exists — aborting.")

    default_dept = session.exec(
        select(Department).where(Department.alias_bangla == "Default")
    ).first()
    if not default_dept:
        raise RuntimeError("Default department not found — run department seeds first.")

    # The JSON's `president` field is a bare string, unlike `members[]` which
    # carry department_alias/is_external. We default it to the প্রশাসন
    # (Administration) department; adjust here if that alias doesn't exist yet.
    president_card = _get_or_create_participant(
        session, data["president"], department_alias="প্রশাসন",
        is_external=False, default_dept_id=default_dept.id, report=report,
    )

    meeting = Meeting(
        serial_num=data["meeting_serial"],
        is_academic=data["is_academic"],
        title=data["meeting_title"],
        description=data.get("description"),
        conclusion=data.get("conclusion"),
        meeting_date=datetime.fromisoformat(data["date"]),
        president_card_id=president_card.id,
        is_finished=True,
    )
    session.add(meeting)
    session.flush()

    for m in data.get("members", []):
        card = _get_or_create_participant(
            session, m["content"], m.get("department_alias"),
            m.get("is_external", False), default_dept.id, report,
        )
        meeting.members.append(card)

    for a in data.get("agenda", []):
        agendum = Agendum(
            meeting_id=meeting.id,
            serial=a["no"],
            body=_doc_from_plain_text(a["content"]),
            is_supplementary=a.get("is_suppli", False),
        )
        session.add(agendum)
        session.flush()

        if a.get("resolution_contents"):
            session.add(
                Resolution(
                    agendum_id=agendum.id,
                    body=_doc_from_plain_text(a["resolution_contents"]),
                )
            )

    report.append(
        f"  + meeting #{meeting.serial_num} created with "
        f"{len(data.get('members', []))} member link(s) and "
        f"{len(data.get('agenda', []))} agenda item(s)"
    )
    return meeting


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("json_path", type=Path, help="Path to a meeting JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Validate and report, but roll back instead of committing")
    args = parser.parse_args()

    data = json.loads(args.json_path.read_text(encoding="utf-8"))
    init_db()  # no-op if tables already exist

    report: list[str] = []
    with Session(engine) as session:
        try:
            meeting = import_meeting(session, data, report)
            if args.dry_run:
                session.rollback()
                report.append("  (dry run — rolled back, nothing was written)")
            else:
                session.commit()
                report.append(f"  ✅ committed meeting id={meeting.id}")
        except Exception as e:
            session.rollback()
            print(f"❌ Import failed: {e}")
            sys.exit(1)

    print("\n".join(report))


if __name__ == "__main__":
    main()
