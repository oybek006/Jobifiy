from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.profile import CandidateProfile, CompanyProfile
from app.schemas.user import (
    UserRegister, UserLogin, TokenResponse,
    RefreshTokenRequest, ChangePasswordRequest, UserOut
)
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=201,
             summary="Yangi foydalanuvchi ro'yxatdan o'tish")
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu email allaqachon ro'yxatdan o'tgan")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Role ga qarab profile yaratish
    if data.role == UserRole.CANDIDATE:
        profile = CandidateProfile(user_id=user.id)
        db.add(profile)
        db.commit()
    elif data.role == UserRole.HR:
        profile = CompanyProfile(user_id=user.id, company_name=data.full_name)
        db.add(profile)
        db.commit()

    return user

@router.post("/login", response_model=TokenResponse,
             summary="Tizimga kirish")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email yoki parol noto'g'ri",
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Akkaunt bloklangan")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse,
             summary="Tokenni yangilash")
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = decode_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Yaroqsiz refresh token")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Foydalanuvchi topilmadi")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    new_refresh = create_refresh_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=access_token, refresh_token=new_refresh)


@router.post("/change-password", summary="Parolni o'zgartirish")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Eski parol noto'g'ri")

    current_user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Parol muvaffaqiyatli o'zgartirildi"}


@router.get("/me", response_model=UserOut, summary="Joriy foydalanuvchi ma'lumoti")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout", summary="Tizimdan chiqish")
def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Muvaffaqiyatli chiqildi"}
