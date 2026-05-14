# 🚀 Jobify — Ish Topish Platformasi

FastAPI asosida qurilgan professional ish topish platformasi. Ish beruvchilar (HR/Company) va ish qidiruvchilar (Candidate) o'rtasidagi ko'prik.

---

## 📋 Texnologiyalar

| Texnologiya | Maqsad |
|-------------|--------|
| **FastAPI** | Backend framework |
| **PostgreSQL** | Asosiy ma'lumotlar bazasi |
| **SQLAlchemy** | ORM |
| **Alembic** | DB migratsiyalari |
| **JWT** | Authentication |
| **Celery + Redis** | Asinxron vazifalar (email) |
| **Docker** | Konteynerizatsiya |

---

## 👥 Foydalanuvchi Rollari

| Rol | Vakolat |
|-----|---------|
| **Admin** | Barcha foydalanuvchilar va vakansiyalarni boshqaradi, statistika ko'radi |
| **HR / Company** | Vakansiya yaratadi, arizalarni ko'rib chiqadi, status o'zgartiradi |
| **Candidate** | Profil to'ldiradi, resume yuklaydi, vakansiyalarga apply qiladi |

---

## 🚀 Ishga Tushirish

### Docker bilan (tavsiya etiladi)

```bash
# 1. Repozitoriyani klonlash
git clone https://github.com/username/jobify.git
cd jobify

# 2. .env faylini sozlash
cp .env.example .env
# .env faylini tahrirlang

# 3. Docker Compose ishga tushirish
docker-compose up -d --build

# 4. Birinchi adminni yaratish
docker exec jobify_api python scripts/create_admin.py
```

### Local (virtual env)

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

pip install -r requirements.txt

# .env faylini sozlang
cp .env.example .env

# Migratsiyalar
alembic upgrade head

# Admin yaratish
python scripts/create_admin.py

# Serverni ishga tushirish
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Celery worker (alohida terminalda)
celery -A app.services.celery_app worker --loglevel=info
```

---

## 🔗 API Endpointlar

### Authentication
| Method | URL | Tavsif | Ruxsat |
|--------|-----|--------|--------|
| POST | `/api/v1/auth/register` | Ro'yxatdan o'tish | Hammaga |
| POST | `/api/v1/auth/login` | Tizimga kirish | Hammaga |
| POST | `/api/v1/auth/refresh` | Token yangilash | Hammaga |
| POST | `/api/v1/auth/logout` | Chiqish | Auth |
| POST | `/api/v1/auth/change-password` | Parol o'zgartirish | Auth |
| GET | `/api/v1/auth/me` | Joriy user | Auth |

### Profile
| Method | URL | Tavsif | Ruxsat |
|--------|-----|--------|--------|
| GET | `/api/v1/profile/candidate` | Kandidat profilini ko'rish | Candidate |
| PUT | `/api/v1/profile/candidate` | Profil yangilash | Candidate |
| POST | `/api/v1/profile/candidate/avatar` | Avatar yuklash | Candidate |
| GET | `/api/v1/profile/company` | Kompaniya profili | HR |
| PUT | `/api/v1/profile/company` | Kompaniya profili yangilash | HR |
| POST | `/api/v1/profile/company/logo` | Logo yuklash | HR |

### Resume
| Method | URL | Tavsif | Ruxsat |
|--------|-----|--------|--------|
| GET | `/api/v1/resumes/` | Resumelar ro'yxati | Candidate |
| POST | `/api/v1/resumes/` | Yangi resume | Candidate |
| GET | `/api/v1/resumes/{id}` | Resume ko'rish | Candidate/HR |
| PUT | `/api/v1/resumes/{id}` | Resume yangilash | Candidate |
| DELETE | `/api/v1/resumes/{id}` | Resume o'chirish | Candidate |
| POST | `/api/v1/resumes/{id}/upload-pdf` | PDF yuklash | Candidate |

### Vacancy
| Method | URL | Tavsif | Ruxsat |
|--------|-----|--------|--------|
| GET | `/api/v1/vacancies/` | Vakansiyalar (search+filter) | Hammaga |
| POST | `/api/v1/vacancies/` | Yangi vakansiya | HR/Admin |
| GET | `/api/v1/vacancies/my` | O'z vakansiyalari | HR |
| GET | `/api/v1/vacancies/{id}` | Vakansiya ko'rish | Hammaga |
| PUT | `/api/v1/vacancies/{id}` | Yangilash | HR/Admin |
| DELETE | `/api/v1/vacancies/{id}` | O'chirish | HR/Admin |

### Apply
| Method | URL | Tavsif | Ruxsat |
|--------|-----|--------|--------|
| POST | `/api/v1/apply/{vacancy_id}` | Ariza topshirish | Candidate |
| GET | `/api/v1/apply/my` | Mening arizalarim | Candidate |
| GET | `/api/v1/apply/vacancy/{id}` | Vakansiya arizalari | HR |
| PUT | `/api/v1/apply/{id}/status` | Status o'zgartirish | HR |
| DELETE | `/api/v1/apply/{id}` | Qaytarib olish | Candidate |

### Admin Panel
| Method | URL | Tavsif |
|--------|-----|--------|
| GET | `/api/v1/admin/stats` | Statistika |
| GET | `/api/v1/admin/users` | Foydalanuvchilar |
| PUT | `/api/v1/admin/users/{id}/block` | Bloklash |
| DELETE | `/api/v1/admin/users/{id}` | O'chirish |
| POST | `/api/v1/admin/users/create-admin` | Admin yaratish |
| GET | `/api/v1/admin/vacancies` | Barcha vakansiyalar |
| PUT | `/api/v1/admin/vacancies/{id}/status` | Status o'zgartirish |

---

## 📊 Swagger & Redoc

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Flower (Celery monitor): http://localhost:5555

---

## ⚙️ .env Sozlamalari

```env
DATABASE_URL=postgresql://postgres:password@db:5432/jobify
SECRET_KEY=your-super-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
REDIS_URL=redis://redis:6379/0
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=your_email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAX_FILE_SIZE_MB=5
```

---

## 🗃️ Database Modellari

```
User ──┬── CandidateProfile
       ├── CompanyProfile
       ├── Resume ──── Apply
       ├── Vacancy ─── Apply
       ├── Favorite
       └── Notification
```

---

## ✅ Validatsiyalar

- Kandidat bir vakansiyaga faqat **1 marta** apply qila oladi
- Deadline o'tgan vakansiyaga apply **qilib bo'lmaydi**
- Resume faqat **PDF** format (max **5MB**)
- Parol minimum **8 belgi**
- Ro'yxatdan o'tishda **admin** roli tanlash mumkin emas

---

## 🏆 Baholash Mezoni

| Mezon | Ball |
|-------|------|
| Authentication | 10 |
| Models | 15 |
| CRUD | 20 |
| Permissions | 15 |
| Filtering/Search | 10 |
| Apply System | 15 |
| Code Quality | 10 |
| Swagger | 5 |
| **Jami** | **100** |
