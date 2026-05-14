from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.apply import ApplyStatus


class ApplyCreate(BaseModel):
    resume_id: Optional[int] = None
    cover_letter: Optional[str] = None


class ApplyStatusUpdate(BaseModel):
    status: ApplyStatus
    hr_note: Optional[str] = None


class ApplyOut(BaseModel):
    id: int
    candidate_id: int
    vacancy_id: int
    resume_id: Optional[int]
    cover_letter: Optional[str]
    status: ApplyStatus
    hr_note: Optional[str]
    applied_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplyListOut(BaseModel):
    items: List[ApplyOut]
    total: int
    page: int
    size: int
    pages: int
