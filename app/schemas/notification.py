from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.notification import NotificationType


class NotificationOut(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: NotificationType
    is_read: bool
    related_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListOut(BaseModel):
    items: List[NotificationOut]
    total: int
    unread_count: int
