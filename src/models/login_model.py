from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginData(BaseModel):
    model_config = {"populate_by_name": True}

    password: str = Field(default="", exclude=True)
    access_token: str
    user_id: Optional[str] = None
    expiration_time: str
    message: str = ""
    address: Optional[str] = None
    phone: Optional[str] = None


class LoginResponse(BaseModel):
    status_code: int
    data: LoginData
