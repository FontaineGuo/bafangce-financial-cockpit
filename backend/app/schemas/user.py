"""
用户相关schemas
"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础信息"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """用户创建"""
    password: str = Field(..., min_length=6, max_length=72)


class UserLogin(BaseModel):
    """用户登录"""
    username: str
    password: str


class User(UserBase):
    """用户信息"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌"""
    access_token: str
    token_type: str = "bearer"
