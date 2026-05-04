from fastapi import APIRouter, Depends, HTTPException,Request,UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database import get_db
from app.core.security import hash_password, create_access_token, create_refresh_token,verify_password
from app.utils.otp_generator import generate_otp, get_otp_expiry
from app.utils.email_sending import send_email
from app.models.user import User
from app.models.otp import OTP
from app.models.refresh_token import RefreshToken
from app.services.google_auth import verify_google_token
from app.core.limiter import limiter
from datetime import timedelta
from app.utils.image_file_name import generate_image_name
from app.utils.current_user_token_check import get_current_user
from app.schemas.user import UserCreate,LoginRequest, OTPVerifyRequest, ResetPasswordSchema, OTPVerifySchema,EmailSchema, GoogleLoginSchema, ProfileUpdateSchema, LogoutDeviceSchema, RefreshRequest
import uuid
import shutil
import os



router = APIRouter()
MAX_ATTEMPTS = 5
LOCK_TIME_MINUTES = 10


# image save folder
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -------------------------
# REGISTER USER
# -------------------------
@router.post("/register")
def register(
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(None),
    mobile: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):

    # ---------------- check existing user ----------------
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    # ---------------- save image ----------------
    image_path = None

    if image:
        ext = image.filename.split(".")[-1]

        filename = generate_image_name(email, ext)
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(image.file.read())

        image_path = file_path

    # ---------------- create user ----------------
    user = User(
        email=email,
        hashed_password=hash_password(password),
        name=name,
        mobile=mobile,
        profile_pic=image_path,
        is_verified=False,
        auth_provider="email"
    )



    db.add(user)
    db.commit()
    db.refresh(user)

    # ---------------- OTP generate ----------------
    otp_code = generate_otp()

    otp = OTP(
        user_id=user.id,
        code=otp_code,
        expires_at=get_otp_expiry()
    )

    db.add(otp)
    db.commit()

    send_email(email, otp_code)

    return {
        "message": "OTP sent to email",
        "user_id": user.id
    }

# -------------------------
# VERIFY OTP
# -------------------------
@router.post("/verify-otp")
def verify_otp(
    data: OTPVerifyRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = (
        db.query(OTP)
        .filter(OTP.user_id == user.id)
        .order_by(OTP.id.desc())
        .first()
    )

    if not otp:
        raise HTTPException(status_code=400, detail="OTP not found")

    # expiry check
    if otp.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired")

    if otp.code != data.code:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user.is_verified = True
    db.delete(otp)
    db.commit()

    return {"message": "Account verified successfully"}


# ---------------- GOOGLE LOGIN ----------------
@router.post("/google")
def google_login(
    user_info: GoogleLoginSchema,
    db: Session = Depends(get_db)
):
    id_token = user_info.id_token
    device_id = user_info.device_id

    if not user_info:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    email = user_info["email"]

    if not email:
        raise HTTPException(status_code=400, detail="Email not found")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(
            email=email,
            hashed_password=None,
            is_verified=True,
            auth_provider="google",
            created_at=datetime.now(timezone.utc)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_login = datetime.now(timezone.utc)
        db.commit()

    # -------------------------
    # TOKENS
    # -------------------------
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )

    # -------------------------
    # SAVE REFRESH TOKEN (NEW)
    # -------------------------
    db_token = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        device_id=device_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )

    db.add(db_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email
        }
    }




@router.post("/login")
@limiter.limit("5/minute")
def login(
    request: Request,
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    email = data.email
    password = data.password
    device_id = data.device_id

    # ---------------- USER FETCH ----------------
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ---------------- LOCK CHECK ----------------
    if user.is_locked:
        if user.lock_until and user.lock_until > datetime.now(timezone.utc):
            raise HTTPException(status_code=403, detail="Account locked")
        else:
            user.is_locked = False
            user.failed_attempts = 0
            user.lock_until = None

    # ---------------- PASSWORD CHECK ----------------
    if not verify_password(password, user.hashed_password):

        user.failed_attempts += 1

        if user.failed_attempts >= 5:
            user.is_locked = True
            user.lock_until = datetime.now(timezone.utc) + timedelta(minutes=10)

        db.commit()

        raise HTTPException(status_code=400, detail="Invalid password")

    # ---------------- SUCCESS LOGIN RESET ----------------
    user.failed_attempts = 0
    user.is_locked = False
    user.lock_until = None
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    # ---------------- TOKENS ----------------
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )

    # ---------------- SAVE REFRESH TOKEN ----------------
    db_token = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        device_id=device_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )

    db.add(db_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email
        }
    }




@router.put("/profile/update")
def update_profile(
    data: ProfileUpdateSchema,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    # ---------------- EMAIL UPDATE ----------------
    if data.email:
        existing = db.query(User).filter(User.email == data.email).first()

        if existing and existing.id != user.id:
            raise HTTPException(status_code=400, detail="Email already taken")

        user.email = data.email

    # ---------------- NAME UPDATE ----------------
    if data.name:
        user.name = data.name

    # ---------------- MOBILE UPDATE ----------------
    if data.mobile:
        existing_mobile = db.query(User).filter(User.mobile == data.mobile).first()

        if existing_mobile and existing_mobile.id != user.id:
            raise HTTPException(status_code=400, detail="Mobile already taken")

        user.mobile = data.mobile

    # ---------------- PASSWORD CHANGE ----------------
    if data.new_password:

        if not data.current_password:
            raise HTTPException(status_code=400, detail="Current password required")

        if not verify_password(data.current_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Current password is wrong")

        user.hashed_password = hash_password(data.new_password)

    # ---------------- UPDATED TIME ----------------
    user.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)

    return {
        "message": "Profile updated successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "mobile": user.mobile,
            "profile_pic": user.profile_pic
        }
    }


# ---------------- PROFILE IMAGE UPLOAD ----------------
@router.put("/profile/upload-photo")
def upload_profile_pic(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)   # 🔥 TOKEN USER
):

    # ---------------- VALIDATION ----------------
    if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid image format")

    # ---------------- FILE NAME ----------------
    ext = image.filename.split(".")[-1]
    filename = generate_image_name(user.email, ext)

    upload_dir = "uploads/profile_pics"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, filename)

    # ---------------- SAVE FILE ----------------
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # ---------------- SAVE DB ----------------
    user.profile_pic = file_path
    user.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)

    return {
        "message": "Profile picture uploaded successfully",
        "profile_pic": file_path
    }


# ---------------- GET PROFILE ----------------
@router.get("/profile")
def get_profile(
    user: User = Depends(get_current_user)
):
    return {
        "message": "Profile fetched successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "mobile": user.mobile,
            "is_verified": user.is_verified,
            "auth_provider": user.auth_provider,
            "profile_pic": user.profile_pic,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
    }



@router.post("/logout-device")
def logout_device(
    data: LogoutDeviceSchema,
    db: Session = Depends(get_db)
):

    token = db.query(RefreshToken).filter(
        RefreshToken.token == data.refresh_token,
        RefreshToken.device_id == data.device_id
    ).first()

    if not token:
        raise HTTPException(status_code=404, detail="Session not found")

    token.is_revoked = True
    db.commit()

    return {"message": "Device logged out successfully"}

@router.post("/forgot-password")
def forgot_password(data: EmailSchema, db: Session = Depends(get_db)):
    email = data.email

    user = db.query(User).filter(User.email == email).first()

    if not user:
        # security: don't expose user existence
        return {"message": "If email exists, OTP sent"}

    otp_code = generate_otp()

    otp = OTP(
        user_id=user.id,
        code=otp_code,
        expires_at=get_otp_expiry()
    )

    db.add(otp)
    db.commit()

    send_email(email, otp_code)

    return {"message": "OTP sent to email"}



@router.post("/reset-password/verify-otp")
def verify_reset_otp(data: OTPVerifySchema, db: Session = Depends(get_db)):
    email = data.email
    code = data.code

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = db.query(OTP).filter(
        OTP.user_id == user.id
    ).order_by(OTP.id.desc()).first()

    if not otp:
        raise HTTPException(status_code=400, detail="OTP not found")

    if otp.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired")

    if otp.code != code:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # ---------------- IMPORTANT FIX ----------------
    reset_token = str(uuid.uuid4())

    user.reset_token = reset_token
    user.reset_token_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)

    db.delete(otp)
    db.commit()

    return {
        "message": "OTP verified",
        "reset_token": reset_token   # 🔥 THIS WAS MISSING
    }

@router.post("/reset-password")
def reset_password(data: ResetPasswordSchema, db: Session = Depends(get_db)):
    email = data.email
    reset_token = data.reset_token
    new_password = data.new_password

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ---------------- TOKEN CHECK ----------------
    if not user.reset_token:
        raise HTTPException(status_code=403, detail="Invalid reset flow")

    if user.reset_token != reset_token:
        raise HTTPException(status_code=403, detail="Invalid token")

    if not user.reset_token_expiry:
        raise HTTPException(status_code=403, detail="Token missing")

    # 🔥 FIX HERE (IMPORTANT)
    if to_utc(user.reset_token_expiry) < datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="Token expired")

    # ---------------- UPDATE PASSWORD ----------------
    user.hashed_password = hash_password(new_password)

    # ---------------- CLEAR TOKEN ----------------
    user.reset_token = None
    user.reset_token_expiry = None

    db.commit()

    return {"message": "Password reset successful"}


@router.post("/refresh-token")
def refresh_token(
    request: RefreshRequest,
    db: Session = Depends(get_db)
):

    data = request.json()
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token missing")

    # ---------------- FIND TOKEN IN DB ----------------
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token,
        RefreshToken.is_revoked == False
    ).first()

    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # ---------------- CHECK EXPIRY ----------------
    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    # ---------------- GET USER ----------------
    user = db_token.user

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ---------------- CREATE NEW ACCESS TOKEN ----------------
    new_access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }




def to_utc(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt