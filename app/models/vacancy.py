import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Enum, Numeric
from sqlalchemy.orm import relationship
from app.db.database import Base


class JobType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    REMOTE = "remote"
    HYBRID = "hybrid"


class ExperienceLevel(str, enum.Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    ANY = "any"


class VacancyStatus(str, enum.Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    DRAFT = "draft"


class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, index=True)
    hr_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    requirements = Column(Text)
    responsibilities = Column(Text)
    skills_required = Column(Text)
    location = Column(String(255))
    is_remote = Column(Boolean, default=False)
    job_type = Column(Enum(JobType), default=JobType.FULL_TIME)
    experience_level = Column(Enum(ExperienceLevel), default=ExperienceLevel.ANY)
    salary_min = Column(Numeric(12, 2))
    salary_max = Column(Numeric(12, 2))
    currency = Column(String(10), default="USD")
    status = Column(Enum(VacancyStatus), default=VacancyStatus.ACTIVE)
    deadline = Column(DateTime)
    views_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hr = relationship("User", back_populates="vacancies")
    applications = relationship("Apply", back_populates="vacancy")
    favorites = relationship("Favorite", back_populates="vacancy")

    def __repr__(self):
        return f"<Vacancy {self.title}>"
