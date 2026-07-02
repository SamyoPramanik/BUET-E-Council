from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import get_current_user
from app.models import Faculty, Department
from app.schemas.organisation import FacultyRead, DepartmentRead

router = APIRouter(tags=["Organisation"])


@router.get("/faculties", response_model=list[FacultyRead])
def get_faculties(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """List all faculties, ordered by display order — used to populate filter dropdowns."""
    faculties = session.exec(select(Faculty).order_by(Faculty.order)).all()
    return [
        FacultyRead(id=f.id, name=f.name_english or f.name_bangla, order=f.order)
        for f in faculties
    ]


@router.get("/departments", response_model=list[DepartmentRead])
def get_departments(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """List all departments — used to populate filter dropdowns (dependent on faculty)."""
    departments = session.exec(select(Department)).all()
    return [
        DepartmentRead(id=d.id, name=d.name_english or d.name_bangla, faculty_id=d.faculty_id)
        for d in departments
    ]
