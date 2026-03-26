from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, SecretStr

from schemas.role_schema import RoleVO


class UserInfoVO(BaseModel):
    uid: int
    uname: str
    avatar: str = None
    email: Optional[str] = None
    created_at: datetime
    login_at: Optional[datetime] = None
    role: Optional[str] = None

    class Config:
        from_attributes = True  # 允许从 ORM 模型转换
        json_encoders = {datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')}  # 规范时间格式


class UserInfoUpdate(BaseModel):
    uid: int
    avatar: str = None
    updated_by: str = None


class UserUpdate(BaseModel):
    uid: Optional[int] = None
    uname: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    rid: Optional[int] = None
    avatar: Optional[str] = None
    updated_by: Optional[str] = None


class UserCreate(BaseModel):
    uname: str = None
    email: str = None
    password: str = None
    status: str = None
    rid: int = None
    avatar: str = None
    created_by: str = None
    updated_by: str = None


class PasswordReset(BaseModel):
    uid: int
    updated_by: str
    password: str


class UserRegister(BaseModel):
    uname: str
    email: EmailStr
    verifyCode: str
    password: str


class UserLogin(BaseModel):
    uname: str
    password: SecretStr


class UserLoginDTO(BaseModel):
    uname: str
    password: SecretStr
    login_ip: str
    login_at: datetime


class UserLoginResponse(BaseModel):
    uname: str
    avatar: str
    token: str


class UserReset(BaseModel):
    uname: str
    password: str


class UserResetVerify(BaseModel):
    uname: str
    email: EmailStr
    verifyCode: str


# 创建用户请求模型
# class UserCreate(BaseModel):
#     uname: str
#     password: str
#     email: EmailStr  # 确保 email 符合格式


# 用户返回数据模型
class UserAdminVO(BaseModel):
    uid: int
    uname: str
    email: Optional[str] = None
    created_at: datetime
    created_by: str = None
    updated_at: datetime
    updated_by: str = None
    avatar: str = None
    status: str = None
    login_ip: Optional[str] = None
    login_at: Optional[datetime] = None
    role: RoleVO = None

    class Config:
        from_attributes = True  # 允许从 ORM 模型转换
        json_encoders = {datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')}  # 规范时间格式


class UserResponse(BaseModel):
    uid: int
    uname: str
    email: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    avatar: str = None

    class Config:
        from_attributes = True  # 允许从 ORM 模型转换
        json_encoders = {datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')}  # 规范时间格式


class UserPage(BaseModel):
    total: int
    users: list[UserAdminVO]  # 使用 UserAdminVO 作为列表元素类型
