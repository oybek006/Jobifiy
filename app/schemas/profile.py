from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime, date


class CandidateProfileUpdate(BaseModel):
    phone: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    experience_years: Optional[int] = None
    education: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    date_of_birth: Optional[date] = None


class CandidateProfileOut(BaseModel):
    id: int
    user_id: int
    phone: Optional[str]
    bio: Optional[str]
    skills: Optional[str]
    experience_years: Optional[int]
    education: Optional[str]
    location: Optional[str]
    linkedin_url: Optional[str]
    github_url: Optional[str]
    avatar_url: Optional[str]
    date_of_birth: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True


class CompanyProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    employee_count: Optional[str] = None
    founded_year: Optional[int] = None


class CompanyProfileOut(BaseModel):
    id: int
    user_id: int
    company_name: str
    description: Optional[str]
    industry: Optional[str]
    website: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    city: Optional[str]
    country: Optional[str]
    logo_url: Optional[str]
    employee_count: Optional[str]
    founded_year: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
