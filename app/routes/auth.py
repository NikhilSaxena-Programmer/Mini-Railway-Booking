from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.models import User
from app.schemas.auth import RegisterSchema, LoginSchema, TokenSchema, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

bearer = HTTPBearer()


@router.post("/register", response_model=UserResponse)
def register(data: RegisterSchema, db: Session = Depends(get_db)):

    email = data.email.lower()

    user = User(name=data.name, email=email, password_hash=hash_password(data.password))

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email already registered")

    return user


@router.post("/login", response_model=TokenSchema)
def login(data: LoginSchema, db: Session = Depends(get_db)):

    user = db.scalar(select(User).where(User.email == data.email.lower()))

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")

    token = create_access_token(user.id)

    return {"access_token": token, "token_type": "bearer"}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
):
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(401, "Invalid or expired token")

    user = db.get(User, user_id)

    if not user:
        raise HTTPException(401, "User not found")

    return user


@router.get("/me", response_model=UserResponse)
def get_profile(user: User = Depends(get_current_user)):
    return user
