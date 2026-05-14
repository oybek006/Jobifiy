from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.vacancy import Vacancy, VacancyStatus, JobType, ExperienceLevel
from app.schemas.vacancy import VacancyCreate, VacancyUpdate, VacancyOut, VacancyListOut
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/vacancies", tags=["Vacancy"])


@router.get("/", response_model=VacancyListOut, summary="Barcha vakansiyalar (search + filter)")
def list_vacancies(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Sarlavha yoki tavsifdan qidirish"),
    location: Optional[str] = Query(None),
    job_type: Optional[JobType] = Query(None),
    experience_level: Optional[ExperienceLevel] = Query(None),
    is_remote: Optional[bool] = Query(None),
    salary_min: Optional[float] = Query(None),
    salary_max: Optional[float] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Vacancy).filter(Vacancy.status == VacancyStatus.ACTIVE)

    # Search
    if search:
        query = query.filter(
            or_(
                Vacancy.title.ilike(f"%{search}%"),
                Vacancy.description.ilike(f"%{search}%"),
                Vacancy.skills_required.ilike(f"%{search}%"),
            )
        )
    if location:
        query = query.filter(Vacancy.location.ilike(f"%{location}%"))
    if job_type:
        query = query.filter(Vacancy.job_type == job_type)
    if experience_level:
        query = query.filter(Vacancy.experience_level == experience_level)
    if is_remote is not None:
        query = query.filter(Vacancy.is_remote == is_remote)
    if salary_min is not None:
        query = query.filter(Vacancy.salary_min >= salary_min)
    if salary_max is not None:
        query = query.filter(Vacancy.salary_max <= salary_max)

    total = query.count()
    items = query.order_by(Vacancy.created_at.desc()).offset((page - 1) * size).limit(size).all()
    return VacancyListOut(
        items=items, total=total, page=page, size=size,
        pages=(total + size - 1) // size,
    )


@router.post("/", response_model=VacancyOut, status_code=201,
             summary="Yangi vakansiya yaratish (HR)")
def create_vacancy(
    data: VacancyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in [UserRole.HR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Faqat HR yoki Admin uchun")

    vacancy = Vacancy(hr_id=current_user.id, **data.model_dump())
    db.add(vacancy)
    db.commit()
    db.refresh(vacancy)
    return vacancy


@router.get("/my", response_model=VacancyListOut,
            summary="HR ning o'z vakansiyalari")
def get_my_vacancies(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in [UserRole.HR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Faqat HR yoki Admin uchun")

    query = db.query(Vacancy).filter(Vacancy.hr_id == current_user.id)
    total = query.count()
    items = query.order_by(Vacancy.created_at.desc()).offset((page - 1) * size).limit(size).all()
    return VacancyListOut(
        items=items, total=total, page=page, size=size,
        pages=(total + size - 1) // size,
    )


@router.get("/{vacancy_id}", response_model=VacancyOut, summary="Vakansiya ko'rish")
def get_vacancy(
    vacancy_id: int,
    db: Session = Depends(get_db),
):
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vakansiya topilmadi")

    vacancy.views_count += 1
    db.commit()
    db.refresh(vacancy)
    return vacancy


@router.put("/{vacancy_id}", response_model=VacancyOut, summary="Vakansiya yangilash (HR)")
def update_vacancy(
    vacancy_id: int,
    data: VacancyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vakansiya topilmadi")
    if vacancy.hr_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Bu vakansiya sizniki emas")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(vacancy, field, value)
    db.commit()
    db.refresh(vacancy)
    return vacancy


@router.delete("/{vacancy_id}", status_code=204, summary="Vakansiya o'chirish")
def delete_vacancy(
    vacancy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vakansiya topilmadi")
    if vacancy.hr_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Bu vakansiya sizniki emas")
    db.delete(vacancy)
    db.commit()
