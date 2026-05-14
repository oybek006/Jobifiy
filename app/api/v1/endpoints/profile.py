import os
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.profile import CandidateProfile, CompanyProfile
from app.schemas.profile import (
    CandidateProfileUpdate, CandidateProfileOut,
    CompanyProfileUpdate, CompanyProfileOut,
)
from app.core.dependencies import get_current_user
from app.core.config import settings

router = APIRouter(prefix="/profile", tags=["Profile"])

UPLOAD_DIR = "uploads/avatars"
os.makedirs(UPLOAD_DIR, exist_ok=True)



@router.get("/candidate", response_model=CandidateProfileOut,
            summary="Kandidat profilini ko'rish")
def get_candidate_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(status_code=403, detail="Faqat kandidatlar uchun")
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil topilmadi")
    return profile


@router.put("/candidate", response_model=CandidateProfileOut,
            summary="Kandidat profilini yangilash")
def update_candidate_profile(
    data: CandidateProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(status_code=403, detail="Faqat kandidatlar uchun")
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil topilmadi")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/candidate/{user_id}", response_model=CandidateProfileOut,
            summary="Boshqa kandidat profilini ko'rish (HR/Admin)")
def get_candidate_profile_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in [UserRole.HR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="HR yoki Admin uchun")
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == user_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil topilmadi")
    return profile



@router.get("/company", response_model=CompanyProfileOut,
            summary="Kompaniya profilini ko'rish")
def get_company_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.HR:
        raise HTTPException(status_code=403, detail="Faqat HR uchun")
    profile = db.query(CompanyProfile).filter(
        CompanyProfile.user_id == current_user.id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Kompaniya profili topilmadi")
    return profile


@router.put("/company", response_model=CompanyProfileOut,
            summary="Kompaniya profilini yangilash")
def update_company_profile(
    data: CompanyProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.HR:
        raise HTTPException(status_code=403, detail="Faqat HR uchun")
    profile = db.query(CompanyProfile).filter(
        CompanyProfile.user_id == current_user.id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Kompaniya profili topilmadi")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/company/{user_id}", response_model=CompanyProfileOut,
            summary="Kompaniya profilini id bo'yicha ko'rish")
def get_company_profile_by_id(
    user_id: int,
    db: Session = Depends(get_db),
):
    profile = db.query(CompanyProfile).filter(
        CompanyProfile.user_id == user_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Kompaniya profili topilmadi")
    return profile



@router.post("/candidate/avatar", summary="Kandidat avatar yuklash")
async def upload_candidate_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(status_code=403, detail="Faqat kandidatlar uchun")
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Faqat rasm fayllari qabul qilinadi")

    filename = f"avatar_{current_user.id}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    async with aiofiles.open(filepath, "wb") as f:
        content = await file.read()
        await f.write(content)

    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()
    profile.avatar_url = f"/uploads/avatars/{filename}"
    db.commit()
    return {"avatar_url": profile.avatar_url}


@router.post("/company/logo", summary="Kompaniya logosi yuklash")
async def upload_company_logo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.HR:
        raise HTTPException(status_code=403, detail="Faqat HR uchun")
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Faqat rasm fayllari qabul qilinadi")

    filename = f"logo_{current_user.id}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    async with aiofiles.open(filepath, "wb") as f:
        content = await file.read()
        await f.write(content)

    profile = db.query(CompanyProfile).filter(
        CompanyProfile.user_id == current_user.id
    ).first()
    profile.logo_url = f"/uploads/avatars/{filename}"
    db.commit()
    return {"logo_url": profile.logo_url}
