from datetime import datetime, timedelta, timezone
import os

import jwt
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

SECRET_KEY = os.getenv("SECRET_KEY", "development-only-secret-change-before-deployment")

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=1)

    payload = {"sub": str(user_id), "exp": expire}

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
