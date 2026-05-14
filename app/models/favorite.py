from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "vacancy_id", name="uq_user_vacancy_fav"),
    )

    user = relationship("User", back_populates="favorites")
    vacancy = relationship("Vacancy", back_populates="favorites")

    def __repr__(self):
        return f"<Favorite user={self.user_id} vacancy={self.vacancy_id}>"
