from typing import Optional

from pydantic import BaseModel
import uuid as uuid_pkg


class FacultyRead(BaseModel):
    id: uuid_pkg.UUID
    name: str  # computed: name_english or name_bangla — kept for existing dropdown consumers
    order: int
    name_bangla: str
    name_english: Optional[str] = None


class DepartmentRead(BaseModel):
    id: uuid_pkg.UUID
    name: str  # computed: name_english or name_bangla — kept for existing dropdown consumers
    faculty_id: uuid_pkg.UUID
    name_bangla: str
    name_english: Optional[str] = None
    alias_bangla: str
    alias_english: Optional[str] = None


class FacultyCreate(BaseModel):
    order: int
    name_bangla: str
    name_english: Optional[str] = None


class FacultyUpdate(BaseModel):
    order: Optional[int] = None
    name_bangla: Optional[str] = None
    name_english: Optional[str] = None


class DepartmentCreate(BaseModel):
    name_bangla: str
    name_english: Optional[str] = None
    alias_bangla: str
    alias_english: Optional[str] = None
    faculty_id: uuid_pkg.UUID


class DepartmentUpdate(BaseModel):
    name_bangla: Optional[str] = None
    name_english: Optional[str] = None
    alias_bangla: Optional[str] = None
    alias_english: Optional[str] = None
    faculty_id: Optional[uuid_pkg.UUID] = None
