from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from app.db.database import Base


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    phone = Column(String(20))
    bio = Column(Text)
    skills = Column(Text)
    experience_years = Column(Integer, default=0)
    education = Column(String(255))
    location = Column(String(255))
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    avatar_url = Column(String(500))
    date_of_birth = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="candidate_profile")

    def __repr__(self):
        return f"<CandidateProfile user_id={self.user_id}>"


class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    company_name = Column(String(255), nullable=False)
    description = Column(Text)
    industry = Column(String(255))
    website = Column(String(500))
    phone = Column(String(20))
    address = Column(Text)
    city = Column(String(100))
    country = Column(String(100))
    logo_url = Column(String(500))
    employee_count = Column(String(50))
    founded_year = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="company_profile")

    def __repr__(self):
        return f"<CompanyProfile {self.company_name}>"
