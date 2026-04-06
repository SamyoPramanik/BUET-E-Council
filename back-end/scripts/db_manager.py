import sys
import os
from sqlmodel import SQLModel

# Add parent directory to path to find 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine

def reset_db():
    """Drops and recreates all tables defined in models."""
    print("🗑️  Dropping all tables...")
    SQLModel.metadata.drop_all(engine)
    
    print("🏗️  Creating new tables...")
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    reset_db()