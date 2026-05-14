from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.vacancy import Vacancy, VacancyStatus
from app.models.apply import Apply, ApplyStatus
from app.models.notification import Notification, NotificationType
from app.schemas.apply import ApplyCreate, ApplyStatusUpdate, ApplyOut, ApplyListOut
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/apply", tags=["Apply System"])


@router.post("/{vacancy_id}", response_model=ApplyOut, status_code=201,
             summary="Vakansiyaga ariza topshirish (Candidate)")
def apply_to_vacancy(
    vacancy_id: int,
    data: ApplyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(status_code=403, detail="Faqat kandidatlar apply qila oladi")

    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vakansiya topilmadi")
    if vacancy.status != VacancyStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Bu vakansiya yopiq")
    if vacancy.deadline and vacancy.deadline < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Ariza muddati tugagan")

    # Takroriy apply tekshirish
    existing = db.query(Apply).filter(
        Apply.candidate_id == current_user.id,
        Apply.vacancy_id == vacancy_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Siz bu vakansiyaga allaqachon ariza topshirgansiz")

    application = Apply(
        candidate_id=current_user.id,
        vacancy_id=vacancy_id,
        **data.model_dump(),
    )
    db.add(application)
    db.flush()

    notification = Notification(
        user_id=vacancy.hr_id,
        title="Yangi ariza keldi",
        message=f"{current_user.full_name} sizning '{vacancy.title}' vakansiyangizga ariza topshirdi",
        type=NotificationType.APPLICATION_RECEIVED,
        related_id=application.id,
    )
    db.add(notification)
    db.commit()
    db.refresh(application)
    return application


@router.get("/my", response_model=ApplyListOut,
            summary="Mening arizalarim (Candidate)")
def get_my_applications(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(status_code=403, detail="Faqat kandidatlar uchun")

    query = db.query(Apply).filter(Apply.candidate_id == current_user.id)
    total = query.count()
    items = query.order_by(Apply.applied_at.desc()).offset((page - 1) * size).limit(size).all()
    return ApplyListOut(items=items, total=total, page=page, size=size,
                        pages=(total + size - 1) // size)


@router.get("/vacancy/{vacancy_id}", response_model=ApplyListOut,
            summary="Vakansiyaga kelgan arizalar (HR)")
def get_vacancy_applications(
    vacancy_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[ApplyStatus] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in [UserRole.HR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Faqat HR yoki Admin uchun")

    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vakansiya topilmadi")
    if vacancy.hr_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Bu vakansiya sizniki emas")

    query = db.query(Apply).filter(Apply.vacancy_id == vacancy_id)
    if status:
        query = query.filter(Apply.status == status)

    total = query.count()
    items = query.order_by(Apply.applied_at.desc()).offset((page - 1) * size).limit(size).all()
    return ApplyListOut(items=items, total=total, page=page, size=size,
                        pages=(total + size - 1) // size)


@router.put("/{apply_id}/status", response_model=ApplyOut,
            summary="Ariza statusini o'zgartirish (HR)")
def update_apply_status(
    apply_id: int,
    data: ApplyStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in [UserRole.HR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Faqat HR yoki Admin uchun")

    application = db.query(Apply).filter(Apply.id == apply_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Ariza topilmadi")

    vacancy = db.query(Vacancy).filter(Vacancy.id == application.vacancy_id).first()
    if vacancy.hr_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Bu ariza sizning vakansiyangizga tegishli emas")

    application.status = data.status
    if data.hr_note:
        application.hr_note = data.hr_note

    # Kandidatga notification
    notification = Notification(
        user_id=application.candidate_id,
        title="Ariza holati o'zgardi",
        message=f"'{vacancy.title}' vakansiyasiga arizangiz holati: {data.status.value}",
        type=NotificationType.APPLICATION_STATUS_CHANGED,
        related_id=apply_id,
    )
    db.add(notification)
    db.commit()
    db.refresh(application)
    return application


@router.delete("/{apply_id}", status_code=204, summary="Arizani qaytarib olish")
def withdraw_application(
    apply_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    application = db.query(Apply).filter(
        Apply.id == apply_id,
        Apply.candidate_id == current_user.id,
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Ariza topilmadi")
    if application.status not in [ApplyStatus.PENDING, ApplyStatus.REVIEWING]:
        raise HTTPException(status_code=400, detail="Bu bosqichda arizani qaytarib bo'lmaydi")

    application.status = ApplyStatus.WITHDRAWN
    db.commit()
