from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date


class PersonBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    experience_years: Optional[int] = 0
    expertise_level: Optional[int] = 1


class PersonCreate(BaseModel):
    name: str
    email: str
    department: str
    role: str
    location: str
    experience_years: int = 0
    expertise_level: int = 3



class PersonUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    experience_years: Optional[int] = None
    expertise_level: Optional[int] = None


class Person(PersonBase):
    id: str
    hire_date: Optional[str] = None
    skills: Optional[List[str]] = []
    projects: Optional[List[str]] = []

    class Config:
        from_attributes = True


class PersonWithConnections(Person):
    skills: List[dict] = []
    projects: List[dict] = []
    documents: List[dict] = []
    connections: int = 0
