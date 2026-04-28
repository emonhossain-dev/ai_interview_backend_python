from pydantic import BaseModel

from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    mobile: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str