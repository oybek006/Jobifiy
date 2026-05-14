import os
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.resume import Resume
from app.schemas.resume import ResumeCreate, ResumeUpdate, ResumeOut
from app.core.dependencies import get_current_user
from app.core.config import settings

router = APIRouter(prefix="/resumes", tags=["Resume"])

UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)
MAX_SIZE = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # bytes


@router.get("/", response_model=List[ResumeOut], summary="O'z resumelarini ko'rish")
def get_my_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(status_code=403, detail="Faqat kandidatlar uchun")
    return db.query(Resume).filter(Resume.user_id == current_user.id).all()


@router.post("/", response_model=ResumeOut, status_code=201,
             summary="Yangi resume yaratish")
def create_resume(
    data: ResumeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(status_code=403, detail="Faqat kandidatlar uchun")

    if data.is_primary:
        db.query(Resume).filter(Resume.user_id == current_user.id).update(
            {"is_primary": False}
        )

    resume = Resume(user_id=current_user.id, **data.model_dump())
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("/{resume_id}", response_model=ResumeOut, summary="Resume ko'rish")
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume topilmadi")
    if resume.user_id != current_user.id and current_user.role not in [UserRole.HR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    return resume


@router.put("/{resume_id}", response_model=ResumeOut, summary="Resume yangilash")
def update_resume(
    resume_id: int,
    data: ResumeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume topilmadi")
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bu resume sizniki emas")

    if data.is_primary:
        db.query(Resume).filter(
            Resume.user_id == current_user.id, Resume.id != resume_id
        ).update({"is_primary": False})

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(resume, field, value)
    db.commit()
    db.refresh(resume)
    return resume


@router.delete("/{resume_id}", status_code=204, summary="Resume o'chirish")
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume topilmadi")
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bu resume sizniki emas")
    db.delete(resume)
    db.commit()


@router.post("/{resume_id}/upload-pdf", response_model=ResumeOut,
             summary="Resume PDF faylini yuklash")
async def upload_resume_pdf(
    resume_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume topilmadi")
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bu resume sizniki emas")

    # Faqat PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Faqat PDF fayl yuklash mumkin")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Fayl hajmi {settings.MAX_FILE_SIZE_MB}MB dan oshmasligi kerak"
        )

    filename = f"resume_{current_user.id}_{resume_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    resume.file_url = f"/uploads/resumes/{filename}"
    resume.file_name = file.filename
    resume.file_size = len(content)
    db.commit()
    db.refresh(resume)
    return resume
