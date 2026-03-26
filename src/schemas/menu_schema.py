from typing import List, Optional

from pydantic import BaseModel


class Meta(BaseModel):
    title: str
    auth: Optional[str] = None
    icon: Optional[str] = None
    menu: Optional[bool] = True
    breadcrumb: Optional[bool] = False
    activeMenu: Optional[str] = None


class Route(BaseModel):
    path: Optional[str] = None
    component: Optional[str] = None
    redirect: Optional[str] = None
    name: Optional[str] = None
    meta: Meta = None
    children: Optional[List["Route"]] = None  # 递归类型，定义子菜单


Route.model_rebuild()

from datetime import datetime, timezone, timedelta


class MenuCreate(BaseModel):
    parent_id: Optional[int] = None
    path: Optional[str] = None
    component: Optional[str] = None
    redirect: Optional[str] = None
    name: Optional[str] = None
    title: str
    order_num: Optional[int] = 0
    auth: Optional[str] = None
    icon: Optional[str] = None
    created_by: str = None
    updated_by: str = None
    status: str = None
    type: str = None


class MenuUpdate(BaseModel):
    mid: int
    path: Optional[str] = None
    component: Optional[str] = None
    redirect: Optional[str] = None
    name: Optional[str] = None
    title: str
    order_num: Optional[int] = 0
    auth: Optional[str] = None
    icon: Optional[str] = None
    updated_by: str = None
    status: str = None


# 重建模型，使其支持递归类型
class MenuSchema(BaseModel):
    mid: int
    path: Optional[str] = None
    component: Optional[str] = None
    redirect: Optional[str] = None
    name: Optional[str] = None
    title: str
    order_num: Optional[int] = 0
    auth: Optional[str] = None
    icon: Optional[str] = None
    menu: Optional[bool] = True
    breadcrumb: Optional[bool] = False
    created_at: datetime = None
    created_by: str = None
    updated_by: str = None
    updated_at: datetime = None
    status: str = None
    type: str = None
    children: Optional[List["MenuSchema"]] = None  # 递归类型，定义子菜单

    class Config:
        from_attributes = True  # 允许从 ORM 模型转换
        json_encoders = {
            datetime: lambda v: v.astimezone(timezone(timedelta(hours=+8))).strftime('%Y-%m-%d %H:%M:%S')
        }  # 规范为 UTC-8 时间格式
