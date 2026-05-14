from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ResumeCreate(BaseModel):
    title: str
    summary: Optional[str] = None
    is_primary: bool = False


class ResumeUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    is_primary: Optional[bool] = None


class ResumeOut(BaseModel):
    id: int
    user_id: int
    title: str
    summary: Optional[str]
    file_url: Optional[str]
    file_name: Optional[str]
    file_size: Optional[int]
    is_primary: bool
    created_at: datetime

    class Config:
        from_attributes = True
