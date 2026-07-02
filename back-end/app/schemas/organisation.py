from pydantic import BaseModel
import uuid as uuid_pkg


class FacultyRead(BaseModel):
    id: uuid_pkg.UUID
    name: str
    order: int


class DepartmentRead(BaseModel):
    id: uuid_pkg.UUID
    name: str
    faculty_id: uuid_pkg.UUID
