"""Pydantic 用户相关模型。"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """通用用户字段。"""

    username: str = Field(..., min_length=3, max_length=50)
    address: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """注册请求体。"""

    password: str = Field(..., min_length=6, max_length=30)


class UserRead(UserBase):
    """对外返回的用户信息。"""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """登录请求体。"""

    username: str
    password: str


class Token(BaseModel):
    """登录返回的访问令牌。"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """JWT 内部载荷。"""

    sub: str

