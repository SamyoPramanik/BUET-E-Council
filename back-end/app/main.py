"""Main FastAPI application entry point for the eCouncil engine.

Defines core routers, system monitoring checks, and global exception parameters.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.v1.router import v1_router  # Import the bundled V1 router

from app.database import AsyncSessionLocal as async_session_maker, engine # Import engine
from app.models import metadata # Ensure your Base model metadata is imported
from app.utils.seeder import parse_and_seed_meeting_json

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[STARTUP] Initializing server systems...")
    
    # 1. Force table structure creation block if missing
    async with engine.begin() as conn:
        # This compiles and runs CREATE TABLE IF NOT EXISTS for meeting, member, agendum, etc.
        await conn.run_sync(metadata.create_all)
    print("[STARTUP] Database structural schema synced successfully.")

    # 2. Proceed with data seeding safely now that tables exist
    async with async_session_maker() as db:
        try:
            summary = await parse_and_seed_meeting_json(
                folder_name="data/seeds",
                file_name="a_463.json",
                db=db
            )
            print(f"[STARTUP SUCCESS] Database seeded successfully: {summary}")
        except Exception as e:
            print(f"[STARTUP INFO] Seed skipped or handled: {str(e)}")

    yield
    print("[SHUTDOWN] Cleaning up background tasks.")


app = FastAPI(
    title="eCouncil Core API",
    description="Minimalist asynchronous backend engine driving council coordination workflows.",
    version="1.0.0",
    lifespan=lifespan
)

# Mount the entire Version 1 pipeline onto the global API router tree
app.include_router(v1_router, prefix="/api/v1")


@app.get("/health", tags=["Monitoring"])
def health_check():
    """Performs a quick system health evaluation.

    Returns:
        dict: A status summary payload indicating operational readiness.
    """
    return {"status": "healthy"}


@app.get("/", tags=["Root"])
def read_root():
    """Serves the API welcome greeting.

    Returns:
        dict: Basic platform confirmation string.
    """
    return {"message": "Welcome to eCouncil API Engine"}