from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.vacancy import Vacancy
from app.models.favorite import Favorite
from app.schemas.vacancy import VacancyOut
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get("/", response_model=List[VacancyOut], summary="Sevimli vakansiyalar")
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    vacancy_ids = [f.vacancy_id for f in favorites]
    return db.query(Vacancy).filter(Vacancy.id.in_(vacancy_ids)).all()


@router.post("/{vacancy_id}", status_code=201, summary="Vakansiyani sevimlilariga qo'shish")
def add_favorite(
    vacancy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vakansiya topilmadi")

    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.vacancy_id == vacancy_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Allaqachon sevimlilariga qo'shilgan")

    fav = Favorite(user_id=current_user.id, vacancy_id=vacancy_id)
    db.add(fav)
    db.commit()
    return {"message": "Sevimlilariga qo'shildi"}


@router.delete("/{vacancy_id}", status_code=204, summary="Sevimlilardan olib tashlash")
def remove_favorite(
    vacancy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    fav = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.vacancy_id == vacancy_id,
    ).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Sevimlilar ro'yxatida yo'q")
    db.delete(fav)
    db.commit()
