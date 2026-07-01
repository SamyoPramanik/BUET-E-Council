"""Main FastAPI application entry point for the eCouncil engine.

Defines core routers, system monitoring checks, and global exception parameters.
"""

from fastapi import FastAPI
from app.v1.router import v1_router  # Import the bundled V1 router

app = FastAPI(
    title="eCouncil Core API",
    description="Minimalist asynchronous backend engine driving council coordination workflows.",
    version="1.0.0"
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