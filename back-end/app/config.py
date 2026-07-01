import os
from pathlib import Path

# Base workspace directory (points to 'back-end/')
BASE_DIR = Path(__file__).resolve().parent.parent

# Set storage path via environment variable for production flexibility, 
# defaulting safely to 'back-end/storage/uploads' for local development
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "storage" / "uploads"))

# Automated runtime setup: Creates the folder structural tree immediately if missing
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)