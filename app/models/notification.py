import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base


class NotificationType(str, enum.Enum):
    APPLICATION_RECEIVED = "application_received"
    APPLICATION_STATUS_CHANGED = "application_status_changed"
    VACANCY_DEADLINE = "vacancy_deadline"
    PROFILE_VIEW = "profile_view"
    GENERAL = "general"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(Enum(NotificationType), default=NotificationType.GENERAL)
    is_read = Column(Boolean, default=False)
    related_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification user={self.user_id} type={self.type}>"
