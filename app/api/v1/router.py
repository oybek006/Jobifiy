from fastapi import APIRouter
from app.api.v1.endpoints import auth, profile, resume, vacancy, apply, favorite, notification, admin

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(profile.router)
api_router.include_router(resume.router)
api_router.include_router(vacancy.router)
api_router.include_router(apply.router)
api_router.include_router(favorite.router)
api_router.include_router(notification.router)
api_router.include_router(admin.router)
