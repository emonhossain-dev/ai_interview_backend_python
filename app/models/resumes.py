from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # basic resume fields
    title = Column(String, nullable=True)          # e.g. "Software Engineer Resume"
    summary = Column(Text, nullable=True)          # short bio/summary

    # file storage (if you upload pdf/doc)
    file_url = Column(String, nullable=True)


    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # relation
    user = relationship("User", back_populates="resumes")