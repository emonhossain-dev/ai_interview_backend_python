from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.database import Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id        = Column(String, nullable=False, index=True)
    category       = Column(String, nullable=False)
    topics         = Column(String, nullable=False)        # comma-separated
    difficulty     = Column(String, nullable=False, default="Medium")
    question_count = Column(Integer, default=0)
    is_complete    = Column(Boolean, default=False)
    mode           = Column(String, nullable=False, default="In-Person")  # NEW
    score          = Column(Float, nullable=True)                          # NEW
    ended_at       = Column(DateTime(timezone=True), nullable=True)        # NEW
    created_at     = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    messages = relationship(
        "InterviewMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class InterviewMessage(Base):
    __tablename__ = "interview_messages"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id"), nullable=False)
    role       = Column(String, nullable=False)   # "user" | "assistant"
    content    = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    session = relationship("InterviewSession", back_populates="messages")