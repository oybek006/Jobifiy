import enum
from datetime import datetime
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base


class ApplyStatus(str, enum.Enum):
    PENDING = "pending"
    REVIEWING = "reviewing"
    INTERVIEW = "interview"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Apply(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    cover_letter = Column(Text)
    status = Column(Enum(ApplyStatus), default=ApplyStatus.PENDING)
    hr_note = Column(Text)
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("candidate_id", "vacancy_id", name="uq_candidate_vacancy"),
    )

    candidate = relationship("User", back_populates="applications")
    vacancy = relationship("Vacancy", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")

    def __repr__(self):
        return f"<Apply candidate={self.candidate_id} vacancy={self.vacancy_id} status={self.status}>"
