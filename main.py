import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.database import engine, Base

# Barcha modellarni import qilish (Alembic uchun)
import app.models  # noqa

# DB jadvallarini yaratish
Base.metadata.create_all(bind=engine)

# Upload papkalarini yaratish
os.makedirs("uploads/resumes", exist_ok=True)
os.makedirs("uploads/avatars", exist_ok=True)

app = FastAPI(
    title="Jobify API",
    description="""
## Jobify — Ish Topish Platformasi API

### Rollar:
- **Admin** — Platformani to'liq boshqaradi
- **HR / Company** — Vakansiya joylaydi, arizalarni ko'rib chiqadi
- **Candidate** — Ish qidiradi, resume yuklaydi, apply qiladi

### Asosiy imkoniyatlar:
- JWT Authentication (Access + Refresh token)
- Role-based access control
- Vacancy search & filter
- Resume PDF upload (max 5MB)
- Apply system (deadline va takroriy apply tekshiruvi)
- Favorites system
- Notification system
- Admin panel
    """,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static fayllar (upload qilingan fayllar)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routerlarni ulash
app.include_router(api_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
