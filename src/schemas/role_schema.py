from datetime import datetime

from pydantic import BaseModel


class RoleVO(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    status: str

    class Config:
        from_attributes = True  # 允许从 ORM 模型转换
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }


class RoleUpdate(BaseModel):
    id: int
    name: str
    description: str
    updated_by: str = None
    status: str


class RoleCreate(BaseModel):
    name: str
    description: str
    created_by: str = None
    updated_by: str = None
    status: str


class RoleMenuBind(BaseModel):
    rid: int
    menus: list[int]


class RolePage(BaseModel):
    total: int
    roles: list[RoleVO]  # 使用 UserAdminVO 作为列表元素类型
