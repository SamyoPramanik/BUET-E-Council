"""Version 1 Central Router Switchboard.

Aggregates all discrete functional domain sub-routers belonging to the 
V1 API specification into a singular cohesive layout.
"""

from fastapi import APIRouter
from app.v1.routers import users , auth, meetings, agenda, files

v1_router = APIRouter()

# Register the user sub-router onto the central V1 interface
v1_router.include_router(users.router)
v1_router.include_router(auth.router)
v1_router.include_router(meetings.router)
v1_router.include_router(agenda.router)
v1_router.include_router(files.router)