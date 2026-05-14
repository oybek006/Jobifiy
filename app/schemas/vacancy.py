from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.vacancy import JobType, ExperienceLevel, VacancyStatus


class VacancyCreate(BaseModel):
    title: str
    description: str
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    skills_required: Optional[str] = None
    location: Optional[str] = None
    is_remote: bool = False
    job_type: JobType = JobType.FULL_TIME
    experience_level: ExperienceLevel = ExperienceLevel.ANY
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    currency: str = "USD"
    deadline: Optional[datetime] = None

    @field_validator("salary_max")
    @classmethod
    def salary_max_gt_min(cls, v, info):
        if v and info.data.get("salary_min") and v < info.data["salary_min"]:
            raise ValueError("salary_max must be >= salary_min")
        return v


class VacancyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    skills_required: Optional[str] = None
    location: Optional[str] = None
    is_remote: Optional[bool] = None
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    currency: Optional[str] = None
    status: Optional[VacancyStatus] = None
    deadline: Optional[datetime] = None


class VacancyOut(BaseModel):
    id: int
    hr_id: int
    title: str
    description: str
    requirements: Optional[str]
    responsibilities: Optional[str]
    skills_required: Optional[str]
    location: Optional[str]
    is_remote: bool
    job_type: JobType
    experience_level: ExperienceLevel
    salary_min: Optional[Decimal]
    salary_max: Optional[Decimal]
    currency: str
    status: VacancyStatus
    deadline: Optional[datetime]
    views_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class VacancyListOut(BaseModel):
    items: List[VacancyOut]
    total: int
    page: int
    size: int
    pages: int
