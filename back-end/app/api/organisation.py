import uuid as uuid_pkg

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import get_current_user, get_admin_user
from app.models import Faculty, Department, User
from app.schemas.organisation import (
    FacultyRead, DepartmentRead,
    FacultyCreate, FacultyUpdate,
    DepartmentCreate, DepartmentUpdate,
)

router = APIRouter(tags=["Organisation"])


def _faculty_to_read(f: Faculty) -> FacultyRead:
    return FacultyRead(
        id=f.id,
        name=f.name_english or f.name_bangla,
        order=f.order,
        name_bangla=f.name_bangla,
        name_english=f.name_english,
    )


def _department_to_read(d: Department) -> DepartmentRead:
    return DepartmentRead(
        id=d.id,
        name=d.name_english or d.name_bangla,
        faculty_id=d.faculty_id,
        name_bangla=d.name_bangla,
        name_english=d.name_english,
        alias_bangla=d.alias_bangla,
        alias_english=d.alias_english,
    )


# ════════════════════════════════════════════════════════════════════════════
# FACULTIES — read is open to any signed-in user, writes are admin-only.
# Only admins may add/edit/delete faculties, departments, and participants.
# ════════════════════════════════════════════════════════════════════════════

@router.get("/faculties", response_model=list[FacultyRead])
def get_faculties(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """List all faculties, ordered by display order — used to populate filter dropdowns."""
    faculties = session.exec(select(Faculty).order_by(Faculty.order)).all()
    return [_faculty_to_read(f) for f in faculties]


@router.post("/faculties", response_model=FacultyRead, status_code=status.HTTP_201_CREATED)
def create_faculty(
    data: FacultyCreate,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user),
):
    """Admin-only: create a new faculty."""
    conflict = session.exec(
        select(Faculty).where(
            (Faculty.name_bangla == data.name_bangla) | (Faculty.order == data.order)
        )
    ).first()
    if conflict:
        raise HTTPException(
            status_code=400,
            detail="A faculty with this name or display order already exists.",
        )

    faculty = Faculty(**data.model_dump())
    session.add(faculty)
    session.commit()
    session.refresh(faculty)
    return _faculty_to_read(faculty)


@router.patch("/faculties/{faculty_id}", response_model=FacultyRead)
def update_faculty(
    faculty_id: uuid_pkg.UUID,
    data: FacultyUpdate,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user),
):
    """Admin-only: update a faculty's name/order."""
    faculty = session.get(Faculty, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found.")

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="At least one field must be provided.")

    for k, v in updates.items():
        setattr(faculty, k, v)

    session.add(faculty)
    session.commit()
    session.refresh(faculty)
    return _faculty_to_read(faculty)


@router.delete("/faculties/{faculty_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faculty(
    faculty_id: uuid_pkg.UUID,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user),
):
    """Admin-only: delete a faculty (cascades to its departments and their participants)."""
    faculty = session.get(Faculty, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found.")

    session.delete(faculty)
    session.commit()


# ════════════════════════════════════════════════════════════════════════════
# DEPARTMENTS
# ════════════════════════════════════════════════════════════════════════════

@router.get("/departments", response_model=list[DepartmentRead])
def get_departments(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """List all departments — used to populate filter dropdowns (dependent on faculty)."""
    departments = session.exec(select(Department)).all()
    return [_department_to_read(d) for d in departments]


@router.post("/departments", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
def create_department(
    data: DepartmentCreate,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user),
):
    """Admin-only: create a new department under a faculty."""
    if not session.get(Faculty, data.faculty_id):
        raise HTTPException(status_code=404, detail="Faculty not found.")

    conflict = session.exec(
        select(Department).where(
            (Department.name_bangla == data.name_bangla)
            | (Department.alias_bangla == data.alias_bangla)
        )
    ).first()
    if conflict:
        raise HTTPException(
            status_code=400,
            detail="A department with this name or alias already exists.",
        )

    department = Department(**data.model_dump())
    session.add(department)
    session.commit()
    session.refresh(department)
    return _department_to_read(department)


@router.patch("/departments/{department_id}", response_model=DepartmentRead)
def update_department(
    department_id: uuid_pkg.UUID,
    data: DepartmentUpdate,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user),
):
    """Admin-only: update a department's name/alias/faculty."""
    department = session.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found.")

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="At least one field must be provided.")

    if "faculty_id" in updates and not session.get(Faculty, updates["faculty_id"]):
        raise HTTPException(status_code=404, detail="Faculty not found.")

    for k, v in updates.items():
        setattr(department, k, v)

    session.add(department)
    session.commit()
    session.refresh(department)
    return _department_to_read(department)


@router.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    department_id: uuid_pkg.UUID,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user),
):
    """Admin-only: delete a department (cascades to its participant cards)."""
    department = session.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found.")

    session.delete(department)
    session.commit()
