from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base



class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    code = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="otp")