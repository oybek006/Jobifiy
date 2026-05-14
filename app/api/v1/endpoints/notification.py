from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationListOut, NotificationOut
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=NotificationListOut, summary="Bildirishnomalar")
def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).all()

    unread = sum(1 for n in items if not n.is_read)
    return NotificationListOut(items=items, total=len(items), unread_count=unread)


@router.put("/{notification_id}/read", response_model=NotificationOut,
            summary="Bildirishnomani o'qilgan deb belgilash")
def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Bildirishnoma topilmadi")

    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


@router.put("/read-all", summary="Barchasini o'qilgan deb belgilash")
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return {"message": "Barcha bildirishnomalar o'qildi"}
