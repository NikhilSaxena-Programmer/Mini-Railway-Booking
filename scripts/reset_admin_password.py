from getpass import getpass

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import User


email = input("Enter your admin email: ").strip().lower()

new_password = getpass("Enter new password (minimum 10 characters): ")

if len(new_password) < 10:
    raise SystemExit("Password must contain at least 10 characters.")

confirm_password = getpass("Confirm new password: ")

if new_password != confirm_password:
    raise SystemExit("Passwords do not match.")

with SessionLocal() as db:
    admin = db.scalar(select(User).where(User.email == email, User.role == "admin"))

    if not admin:
        raise SystemExit("Admin account not found.")

    admin.password_hash = hash_password(new_password)
    db.commit()

print("Admin password reset successfully!")
