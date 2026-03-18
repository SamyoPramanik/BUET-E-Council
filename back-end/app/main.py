from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api import auth, users, meetings

from .database import init_db, engine
from .admin import setup_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the app starts
    print("🚀 Initializing Database...")
    init_db()
    yield
    # This runs when the app stops
    print("🛑 Shutting down...")

app = FastAPI(title="BUET e-Council API", lifespan=lifespan)

# 1. Define the "Allowed Origins"
origins = [
    settings.FRONTEND_URL,  # http://localhost:3000
    "http://127.0.0.1:3000", # Alternative local address
]

# 2. Add the Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allows your React/Vue app
    allow_credentials=True,           # REQUIRED for cookies/session_id
    allow_methods=["*"],              # Allows GET, POST, DELETE, etc.
    allow_headers=["*"],              # Allows Custom Headers (like Session-ID)
)

# 3. Include your routers after middleware
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(meetings.router)

# Mount the Admin Interface
setup_admin(app, engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to BUET e-Council API", "admin_panel": "/admin"}