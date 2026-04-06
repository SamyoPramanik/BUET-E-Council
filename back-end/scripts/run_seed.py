import pkgutil
import importlib
from sqlmodel import Session, select
from app.database import engine
from db_manager import reset_db
from seeds.users import seed_users
from seeds.departments import get_department_seeds
from seeds.faculties import get_faculty_seeds
from seeds.participants import get_participant_seeds
from app.models import ParticipantCard

# Import the meeting seed packages
import seeds.meetings.academic as academic_seeds
import seeds.meetings.syndicate as syndicate_seeds

import inspect
from sqlmodel import select
from app.models import ParticipantCard, MemberRole, Department


def run_meeting_seeds(session, package):
    """
    Dynamically finds and runs 'get_seed_data' from all modules in a package.

    Supports two signatures:
      - Legacy:  get_seed_data()                          → returns a Meeting
      - Current: get_seed_data(session, participant_map)  → returns a Meeting

    The participant_map is built once (lazily) and reused across all modules.
    Missing ParticipantCards are auto-created with the Default department.
    """
    participant_map = None  # built lazily on first module that needs it
    default_dept_id = None  # fetched lazily alongside participant_map

    for loader, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        if is_pkg:
            continue

        full_module_name = f"{package.__name__}.{module_name}"
        module = importlib.import_module(full_module_name)

        if not hasattr(module, "get_seed_data"):
            continue

        print(f"🌱 Seeding meeting from: {module_name}...")

        fn = module.get_seed_data
        params = inspect.signature(fn).parameters

        if len(params) == 0:
            # Legacy signature: get_seed_data()
            meeting_data = fn()
        else:
            # Current signature: get_seed_data(session, participant_map)
            if participant_map is None:
                participant_map, default_dept_id = _build_participant_map(session)
                print(f"  📋 Loaded {len(participant_map)} participant cards into map.")

            # Wrap the map in a smart resolver before passing to the seed fn
            smart_map = _SmartParticipantMap(
                participant_map, session, default_dept_id
            )
            meeting_data = fn(session, smart_map)

            # Report any auto-created cards after each meeting
            if smart_map.created_cards:
                print(
                    f"  ✨ Auto-created {len(smart_map.created_cards)} new card(s):\n"
                    + "\n".join(f"     • {c}" for c in smart_map.created_cards)
                )

        session.add(meeting_data)

    session.commit()
    print("✅ All meeting seeds committed.")


def _build_participant_map(session) -> tuple:
    """
    Returns (participant_map, default_dept_id).
    participant_map: dict[content_str -> ParticipantCard]
    """
    all_cards = session.exec(select(ParticipantCard)).all()
    participant_map = {p.content: p for p in all_cards}

    default_dept = session.exec(
        select(Department).where(Department.alias_bangla == "Default")
    ).first()

    if default_dept is None:
        raise RuntimeError(
            "Default department not found in DB. Run department seeds first."
        )

    return participant_map, default_dept.id


class _SmartParticipantMap:
    """
    A dict-like wrapper around participant_map that auto-creates missing
    ParticipantCards (with Default department) instead of raising KeyError.

    Behaves like a dict for:
      - `key in map`   → always True  (triggers auto-create on access)
      - `map[key]`     → returns card, creating it if needed
      - `map.get(key)` → same as map[key]
    """

    def __init__(self, participant_map: dict, session, default_dept_id):
        self._map = participant_map
        self._session = session
        self._default_dept_id = default_dept_id
        self._created: list = []  # track auto-created cards for logging

    # ── dict-like interface ───────────────────────────────────────────

    def __contains__(self, key: str) -> bool:
        # Always return True — missing cards are created on __getitem__
        return True

    def __getitem__(self, content: str) -> ParticipantCard:
        if content in self._map:
            return self._map[content]

        # ── Auto-create the missing card ─────────────────────────────
        new_card = ParticipantCard(
            content=content,
            role=MemberRole.REGULAR,
            email=None,
            department_id=self._default_dept_id,
        )
        self._session.add(new_card)
        self._session.flush()  # assigns UUID without full commit

        # Cache so subsequent references in the same run reuse it
        self._map[content] = new_card
        self._created.append(content)

        return new_card

    def get(self, key: str, default=None) -> ParticipantCard:
        """Support map.get(key) pattern used in some seed helpers."""
        return self[key]

    # ── diagnostics ──────────────────────────────────────────────────

    @property
    def created_cards(self) -> list:
        """Content strings that were auto-created during this meeting seed."""
        return list(self._created)

def run_all_seeds():
    # Start with a blank slate
    reset_db()

    with Session(engine) as session:
        try:

            # --- NEW: SEED FACULTIES ---
            print("🏛️ Seeding faculties...")
            faculties = get_faculty_seeds()
            for f in faculties:
                session.add(f)
            
            # Flush so the database assigns/recognizes the IDs 
            # without committing the whole transaction yet
            session.flush() 

            # Create the map: { "name_bangla": UUID }
            faculty_map = {f.name_bangla: f.id for f in faculties}

            # --- NEW: SEED DEPARTMENTS ---
            print("📂 Seeding departments...")
            departments = get_department_seeds(faculty_map)
            for d in departments:
                session.add(d)
            
            session.flush()

            dept_map = {d.name_bangla: d.id for d in departments}

            # 3. Seed Participant Cards
            print("📋 Seeding participant cards...")
            cards = get_participant_seeds(dept_map) # Pass the map here
            for c in cards:
                session.add(c)
            session.flush()

            # 1. Seed Users
            print("👤 Seeding users...")
            seed_users(session)
            
            # 2. Seed Academic Meetings
            print("🏫 Seeding academic meetings...")
            run_meeting_seeds(session, academic_seeds)
            
            # 3. Seed Syndicate Meetings
            print("⚖️ Seeding syndicate meetings...")
            run_meeting_seeds(session, syndicate_seeds)

            session.commit()
            print("\n✅ Database seeding completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            session.rollback()

if __name__ == "__main__":
    run_all_seeds()