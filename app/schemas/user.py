from pydantic import BaseModel

from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    mobile: Optional[str] = None
    current_position: Optional[str] = None

# ✅ Request Schema (JSON Body)
class LoginRequest(BaseModel):
    email: str
    password: str
    device_id: Optional[str] = None


class OTPVerifyRequest(BaseModel):
    email: str
    code: str




class EmailSchema(BaseModel):
    email: str


class OTPVerifySchema(BaseModel):
    email: str
    code: str


class ResetPasswordSchema(BaseModel):
    email: str
    reset_token: str
    new_password: str


class GoogleLoginSchema(BaseModel):
    id_token: str
    device_id: str
    # Google token থেকে frontend পাঠাবে
    email: str
    name: Optional[str] = None
    profile_pic: Optional[str] = None



class ProfileUpdateSchema(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    mobile: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None



class LogoutDeviceSchema(BaseModel):
    device_id: str
    refresh_token: str



class RefreshRequest(BaseModel):
    refresh_token: str