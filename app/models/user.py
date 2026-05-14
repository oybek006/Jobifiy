import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    HR = "hr"
    CANDIDATE = "candidate"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CANDIDATE, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    candidate_profile = relationship("CandidateProfile", back_populates="user", uselist=False)
    company_profile = relationship("CompanyProfile", back_populates="user", uselist=False)
    resumes = relationship("Resume", back_populates="user")
    applications = relationship("Apply", back_populates="candidate")
    favorites = relationship("Favorite", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    vacancies = relationship("Vacancy", back_populates="hr")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
