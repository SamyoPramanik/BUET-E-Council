"""Database connection configuration module for the eCouncil application.

This module initializes the asynchronous SQLAlchemy engine and provides 
a dependency function to manage session lifecycles for incoming API requests.
"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Safely extract and modify the connection URL to use asyncpg
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:buet_admin_pass@db:5432/ecouncil_db")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Initialize the high-performance async engine with connection pooling parameters
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Automatically tests connections before giving them to the API
    echo=False           # Flip to True if you need to debug raw compiled SQL in the terminal
)

# Configuration factory for creating short-lived async database sessions
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency tracking block to yield a database session per API request.

    Guarantees that connection transactions are cleanly closed or rolled back
    automatically when an API request completes.

    Yields:
        AsyncSession: An active transaction-bound database session context.
    """
    async with AsyncSessionLocal() as session:
        yield session