from getpass import getpass

from sqlalchemy import select

from app.core.database import Base, engine, SessionLocal
from app.core.security import hash_password
from app.models import User


# Create database tables if they do not exist
Base.metadata.create_all(bind=engine)

print("\n=== Create Admin Account ===")

name = input("Admin name: ").strip()
email = input("Admin email: ").strip().lower()
password = getpass("Admin password (minimum 10 characters): ")
confirm_password = getpass("Confirm admin password: ")

if len(name) < 2:
    raise SystemExit("Name must contain at least 2 characters.")

if len(password) < 10:
    raise SystemExit("Password must contain at least 10 characters.")

if password != confirm_password:
    raise SystemExit("Passwords do not match.")

with SessionLocal() as db:
    existing_user = db.scalar(select(User).where(User.email == email))

    if existing_user:
        raise SystemExit(
            "This email is already registered. Use the password reset script if needed."
        )

    admin = User(
        name=name, email=email, password_hash=hash_password(password), role="admin"
    )

    db.add(admin)
    db.commit()

    print("\nAdmin account created successfully!")
    print(f"Admin name: {admin.name}")
    print(f"Admin email: {admin.email}")
    print(f"Role: {admin.role}")
