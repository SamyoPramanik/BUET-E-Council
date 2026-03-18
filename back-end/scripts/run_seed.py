import pkgutil
import importlib
from sqlmodel import Session
from app.database import engine
from db_manager import reset_db
from seeds.users import seed_users

# Import the meeting seed packages
import seeds.meetings.academic as academic_seeds
import seeds.meetings.syndicate as syndicate_seeds

def run_meeting_seeds(session, package):
    """Dynamically finds and runs 'get_seed_data' from all modules in a package."""
    for loader, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        if is_pkg:
            continue
        
        # Import the module (e.g., seeds.meetings.academic.a_465)
        full_module_name = f"{package.__name__}.{module_name}"
        module = importlib.import_module(full_module_name)
        
        # Check if it has the get_seed_data function
        if hasattr(module, "get_seed_data"):
            print(f"🌱 Seeding meeting from: {module_name}...")
            meeting_data = module.get_seed_data()
            session.add(meeting_data)

def run_all_seeds():
    # Start with a blank slate
    reset_db()

    with Session(engine) as session:
        try:
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