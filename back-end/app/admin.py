from datetime import datetime, timezone

from fastapi import HTTPException
from sqladmin import ModelView, Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from sqlmodel import Session, select

from .models import User, UserSession
from .database import engine
from .config import settings

from fastapi import HTTPException
from starlette import status

class AdminAuth(AuthenticationBackend):
    async def authenticate(self, request: Request) -> bool:
        session_id = request.cookies.get("session_id")
        
        # 1. No session?
        if not session_id:
            # We RAISE the error. To satisfy the type checker, 
            # this is valid because a 'raise' doesn't return a value.
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                detail="Redirecting to login",
                headers={"Location": f"{settings.FRONTEND_URL}/sign-in?error=session_required"}
            )

        with Session(engine) as db:
            # Note: Using datetime.utcnow() to match your DB storage
            statement = select(User).join(UserSession).where(
                UserSession.id == session_id,
                User.role == "admin",
                UserSession.expires_at > datetime.utcnow()
            )
            admin_user = db.exec(statement).first()
            
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                detail="Unauthorized",
                headers={"Location": f"{settings.FRONTEND_URL}/unauthorized"}
            )
            
        # 2. If everything is perfect, return True
        return True

    async def login(self, request: Request) -> bool:
        # Since we handle redirects in authenticate, 
        # this part just acts as a fallback.
        return True
    
# Initialize the backend
admin_auth = AdminAuth(secret_key="your-very-secret-key")

class UserAdmin(ModelView, model=User):
    # Use strings instead of class attributes to stop the type error
    column_list = ["id", "email", "role", "is_verified"] 
    column_searchable_list = ["email"]
    icon = "fa-solid fa-user"
    category = "Accounts"

class SessionAdmin(ModelView, model=UserSession):
    # Same here for the Session table
    column_list = ["user_id", "ip_address", "expires_at"]
    icon = "fa-solid fa-clock"
    category = "Security"

def setup_admin(app, engine):
    # This mounts the admin panel at /admin
    admin = Admin(
    app, 
    engine, 
    authentication_backend=admin_auth,
    title="e-Council Admin",
    base_url="/admin"
)
    admin.add_view(UserAdmin)
    admin.add_view(SessionAdmin)