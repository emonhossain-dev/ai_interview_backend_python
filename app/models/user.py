from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    mobile = Column(String, nullable=False)
    current_position = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)

    is_verified = Column(Boolean, default=False)
    auth_provider = Column(String, default="email")  # email | google

    is_locked = Column(Boolean, default=False)
    failed_attempts = Column(Integer, default=0)
    lock_until = Column(DateTime, nullable=True)
    last_failed_device = Column(String, nullable=True)

    reset_token = Column(String, nullable=True)
    reset_token_expiry = Column(DateTime(timezone=True))

    profile_pic = Column(String, nullable=True)

    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")


    otp = relationship("OTP", back_populates="user", uselist=False)

    # ✅ NEW: refresh token relation
    refresh_tokens = relationship("RefreshToken", back_populates="user")

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.utcnow)