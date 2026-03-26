from typing import Optional

from pydantic import BaseModel


class DocumentUserVO(BaseModel):
    id: int
    uuid: str
    content: Optional[str] = None
    name: Optional[str] = None

    # Model ID

    class Config:
        from_attributes = True  # 允许从 ORM 模型转换


from datetime import datetime


class DocumentUserMeta(BaseModel):
    id: int
    uuid: str
    type: Optional[str] = None
    name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # 允许从 ORM 模型转换
        json_encoders = {
            datetime: lambda v: v.astimezone(timezone(timedelta(hours=+8))).strftime('%Y-%m-%d %H:%M:%S')
        }


class DocumentUserPage(BaseModel):
    total: int
    documents: list[DocumentUserMeta]


class DocumentUpdate(BaseModel):
    uuid: str
    name: Optional[str] = None
    content: Optional[str] = None
    update_by:Optional[str] = None


class DocumentCreate(BaseModel):
    uuid: str
    # Document ID
    tid: int
    # Document Type ID
    query: str
    # User Query
    mid: int
    content: Optional[str] = None
    name: Optional[str] = None
    uid: Optional[int] = None
    updated_by: Optional[str] = None
    created_by: Optional[str] = None
    # Model ID


from datetime import datetime, timezone, timedelta


class DocTypeUpdate(BaseModel):
    id: int
    label: Optional[str]
    description: Optional[str] = None
    prompt: Optional[str] = None
    example: Optional[str] = None
    updated_by: Optional[str] = None
    status: Optional[str] = None


class DocTypeCreate(BaseModel):
    label: str
    description: Optional[str] = None
    prompt: Optional[str] = None
    example: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    status: str
    fid: Optional[int] = None
    # created_by 由后端通过用户注入拿到后赋值


class DocTypeUserVO(BaseModel):
    id: int
    label: str
    prompt: Optional[str] = None

    class Config:
        from_attributes = True


class DocTypeVO(BaseModel):
    id: int
    label: str
    description: Optional[str] = None
    prompt: Optional[str] = None
    example: Optional[str] = None
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    status: str

    class Config:
        from_attributes = True  # 允许从 ORM 模型转换
        json_encoders = {
            datetime: lambda v: v.astimezone(timezone(timedelta(hours=+8))).strftime('%Y-%m-%d %H:%M:%S')
        }  # 规范为 UTC-8 时间格式
