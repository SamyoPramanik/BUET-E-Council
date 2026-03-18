import os
from sqlmodel import create_engine, Session, SQLModel

# We grab the URL from the environment variable we set in podman-compose
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:buet_admin_pass@db:5432/ecouncil_db")

# The engine is the actual connection pool
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    """Creates the database tables based on our models."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency to get a database session for a request."""
    with Session(engine) as session:
        yield session