from sqlmodel import Session, select
from app.models import User, UserRole
from app.utils import hash_password

# Dev-only default password for seeded accounts. Not used in production —
# real accounts are created via the admin "create user" endpoint, which
# generates/accepts a password and emails it to the user.
SEED_PASSWORD = "changeme123"

def seed_users(session: Session):
    print("👤 Seeding Users...")
    seeded_hash = hash_password(SEED_PASSWORD)
    candidates = [
        User(email="admin@gmail.com", role=UserRole.admin, hashed_password=seeded_hash),
        User(email="staff@gmail.com", role=UserRole.staff, hashed_password=seeded_hash),
        User(email="viewer@gmail.com", role=UserRole.viewer, hashed_password=seeded_hash),
    ]

    existing_emails = set(session.exec(select(User.email)).all())
    users = [u for u in candidates if u.email not in existing_emails]

    session.add_all(users)
    session.commit()
    return users