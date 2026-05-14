"""
Birinchi admin foydalanuvchisini yaratish uchun script.
Ishlatish: python scripts/create_admin.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.core.security import hash_password
import app.models  # noqa

Base.metadata.create_all(bind=engine)

def create_admin():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing:
            print(f"Admin allaqachon mavjud: {existing.email}")
            return

        admin = User(
            email="admin@jobify.uz",
            hashed_password=hash_password("Admin@123456"),
            full_name="Super Admin",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
        )
        db.add(admin)
        db.commit()
        print("✅ Admin muvaffaqiyatli yaratildi!")
        print("   Email: admin@jobify.uz")
        print("   Parol: Admin@123456")
        print("   ⚠️  Parolni darhol o'zgartiring!")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
