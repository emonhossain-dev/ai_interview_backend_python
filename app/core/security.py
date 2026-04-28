from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta,timezone

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

SECRET_KEY = "SUPER_SECRET_KEY"
ALGORITHM = "HS256"


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


# ---------------- ACCESS TOKEN ----------------
def create_access_token(data: dict, expires_delta: int = 1):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire, "type": "access"})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ---------------- REFRESH TOKEN ----------------
def create_refresh_token(data: dict, expires_delta: int = 7):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(days=expires_delta)
    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)