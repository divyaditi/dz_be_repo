from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str
    password: str


class User(BaseModel):
    user_id: str
    user_email: str
    password: str = Field(default="", exclude=True)
    jwt_token: str = ""
    expiration_time: str = ""
    created_at: str = ""
    updated_at: str = ""
    is_active: bool = True


class UserDetail(BaseModel):
    user_detail_id: str
    user_id: str
    address: Optional[str] = None
    phone_no: Optional[str] = None
    pincode: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    is_active: bool = True


class LoginResponse(BaseModel):
    status_code: int
    user_id: Optional[str] = None
    jwt_token: str = ""
    expiration_time: str = ""
    message: str = ""
