import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Chat(Base):
    __tablename__ = "chats"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, user_id, title=None):
        self.id = str(uuid.uuid4())
        self.user_id = str(user_id)
        self.title = title