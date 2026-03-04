from pydantic import BaseModel
from typing import Optional, List


class SkillBase(BaseModel):
    name: str
    category: str
    level: str
    demand: int


class Skill(SkillBase):
    id: str

    class Config:
        from_attributes = True


class SkillWithExperts(Skill):
    expert_count: int = 0
    experts: List[dict] = []


class ProjectBase(BaseModel):
    name: str
    domain: str
    tech_stack: List[str]
    status: str
    budget: int
    priority: str


class Project(ProjectBase):
    id: str
    date: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectWithDetails(Project):
    team_members: List[dict] = []
    technologies: List[dict] = []


class DocumentBase(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    topic: Optional[str] = None
    views: Optional[int] = 0
    rating: Optional[float] = 0.0
    content: Optional[str] = None


class Document(DocumentBase):
    id: str
    author: Optional[str] = None
    date: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentWithDetails(Document):
    author_details: Optional[dict] = None
    related_skills: List[dict] = []
    similar_documents: List[dict] = []


class DocumentCreate(DocumentBase):
    author: str
    date: Optional[str] = None


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    topic: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    views: Optional[int] = None
    rating: Optional[float] = None
    content: Optional[str] = None


class Technology(BaseModel):
    id: str
    uri: str
    name: str
    description: str
    category: str

    class Config:
        from_attributes = True
