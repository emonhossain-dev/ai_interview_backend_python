from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from datetime import datetime, timezone, timedelta

from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.database import get_db
from app.core.security import create_access_token, create_refresh_token
from app.core.config import SECRET_KEY, ALGORITHM


router = APIRouter()

@router.post("/refresh")
def refresh_token_api(
    refresh_token: str,
    device_id: str = None,
    db: Session = Depends(get_db)
):

    stored = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token
    ).first()

    if not stored:
        raise HTTPException(status_code=401, detail="Invalid token")

    if stored.is_revoked:
        raise HTTPException(status_code=401, detail="Token revoked")

    if stored.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Token expired")

    # ---------------- DEVICE CHECK ----------------
    if device_id and stored.device_id and stored.device_id != device_id:
        raise HTTPException(status_code=401, detail="Device mismatch")

    # decode JWT
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid JWT")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ---------------- ROTATION ----------------
    stored.is_revoked = True

    new_refresh = create_refresh_token(
        data={"sub": str(user.id)}
    )

    new_db_token = RefreshToken(
        token=new_refresh,
        user_id=user.id,
        device_id=stored.device_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )

    db.add(new_db_token)

    new_access = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    db.commit()

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer"
    }