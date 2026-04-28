from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.security import create_access_token, create_refresh_token
from app.core.security import verify_password  # assume you already have this

from datetime import datetime, timezone

router = APIRouter()


@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):

    # 1. find user
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. check auth provider (important)
    if user.auth_provider != "email":
        raise HTTPException(
            status_code=400,
            detail=f"Please login using {user.auth_provider}"
        )

    # 3. verify password
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid password")

    # 4. update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # 5. generate tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email
        }
    }