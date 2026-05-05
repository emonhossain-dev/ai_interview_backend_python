from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)

    token = Column(String, unique=True, index=True)

    # ✅ FIX: ForeignKey add
    user_id = Column(Integer, ForeignKey("users.id"))

    is_revoked = Column(Boolean, default=False)

    device_id = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True))

    # ✅ FIX: relationship add
    user = relationship("User", back_populates="refresh_tokens")