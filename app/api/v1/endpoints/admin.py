from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.vacancy import Vacancy, VacancyStatus
from app.models.apply import Apply
from app.models.profile import CandidateProfile, CompanyProfile
from app.schemas.user import UserOut, UserUpdate
from app.schemas.vacancy import VacancyOut, VacancyListOut
from app.schemas.apply import ApplyOut
from app.core.dependencies import get_admin_user
from app.core.security import hash_password
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/admin", tags=["Admin Panel"])



@router.get("/stats", summary="Platforma statistikasi")
def get_stats(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    total_users = db.query(User).count()
    total_candidates = db.query(User).filter(User.role == UserRole.CANDIDATE).count()
    total_hr = db.query(User).filter(User.role == UserRole.HR).count()
    total_vacancies = db.query(Vacancy).count()
    active_vacancies = db.query(Vacancy).filter(Vacancy.status == VacancyStatus.ACTIVE).count()
    total_applications = db.query(Apply).count()

    return {
        "users": {
            "total": total_users,
            "candidates": total_candidates,
            "hr_companies": total_hr,
            "admins": total_users - total_candidates - total_hr,
        },
        "vacancies": {
            "total": total_vacancies,
            "active": active_vacancies,
            "closed": total_vacancies - active_vacancies,
        },
        "applications": {
            "total": total_applications,
        },
    }



@router.get("/users", response_model=List[UserOut], summary="Barcha foydalanuvchilar")
def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = Query(None),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if search:
        query = query.filter(
            User.full_name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%")
        )
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    return query.order_by(User.created_at.desc()).offset((page - 1) * size).limit(size).all()


@router.get("/users/{user_id}", response_model=UserOut, summary="Foydalanuvchi ma'lumoti")
def get_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return user


@router.put("/users/{user_id}", response_model=UserOut, summary="Foydalanuvchini yangilash")
def update_user(
    user_id: int,
    data: UserUpdate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}/block", response_model=UserOut,
            summary="Foydalanuvchini bloklash/blokdan chiqarish")
def toggle_block_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="O'zingizni bloklay olmaysiz")

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    action = "blok olindi" if not user.is_active else "blokdan chiqarildi"
    return user


@router.delete("/users/{user_id}", status_code=204, summary="Foydalanuvchini o'chirish")
def delete_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="O'zingizni o'chira olmaysiz")
    db.delete(user)
    db.commit()


class AdminCreateRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


@router.post("/users/create-admin", response_model=UserOut, status_code=201,
             summary="Yangi admin yaratish")
def create_admin(
    data: AdminCreateRequest,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu email allaqachon mavjud")

    new_admin = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin



@router.get("/vacancies", response_model=VacancyListOut, summary="Barcha vakansiyalar (Admin)")
def admin_list_vacancies(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[VacancyStatus] = Query(None),
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    query = db.query(Vacancy)
    if status:
        query = query.filter(Vacancy.status == status)
    total = query.count()
    items = query.order_by(Vacancy.created_at.desc()).offset((page - 1) * size).limit(size).all()
    return VacancyListOut(items=items, total=total, page=page, size=size,
                          pages=(total + size - 1) // size)


@router.put("/vacancies/{vacancy_id}/status", response_model=VacancyOut,
            summary="Vakansiya statusini o'zgartirish")
def admin_change_vacancy_status(
    vacancy_id: int,
    status: VacancyStatus,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vakansiya topilmadi")
    vacancy.status = status
    db.commit()
    db.refresh(vacancy)
    return vacancy


@router.delete("/vacancies/{vacancy_id}", status_code=204,
               summary="Vakansiyani o'chirish (Admin)")
def admin_delete_vacancy(
    vacancy_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vakansiya topilmadi")
    db.delete(vacancy)
    db.commit()



@router.get("/applications", summary="Barcha arizalar (Admin)")
def admin_list_applications(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    query = db.query(Apply)
    total = query.count()
    items = query.order_by(Apply.applied_at.desc()).offset((page - 1) * size).limit(size).all()
    return {
        "items": [ApplyOut.model_validate(i) for i in items],
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size,
    }
