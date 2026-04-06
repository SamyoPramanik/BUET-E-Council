from sqlmodel import Session
from app.models import User, UserRole

def seed_users(session: Session):
    print("👤 Seeding Users...")
    users = [
        User(email="admin@gmail.com", role=UserRole.admin, is_verified=False),
        User(email="staff@gmail.com", role=UserRole.staff, is_verified=False),
        User(email="viewer@gmail.com", role=UserRole.viewer, is_verified=False),
    ]
    session.add_all(users)
    session.commit()
    return users