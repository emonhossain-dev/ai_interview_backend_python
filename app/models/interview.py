from sqlalchemy import Column, Integer, ForeignKey, String
from app.database import Base

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)
    status = Column(String)