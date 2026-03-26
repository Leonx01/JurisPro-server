from typing import Optional

from pydantic import BaseModel


class PromptTemplate(BaseModel):
    content: str = ''
    slots: list[str] = []


class PromptUpdate(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    fid: int
    prompt: str
    updated_by: Optional[str] = None


class PromptCreate(BaseModel):
    name: str
    description: Optional[str] = None
    fid: int
    prompt: str
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    # created_by 由后端通过用户注入拿到后赋值


from datetime import datetime, timezone, timedelta


class PromptVO(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    fid: int
    prompt: str
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str

    class Config:
        from_attributes = True  # 允许从 ORM 模型转换
        json_encoders = {
            datetime: lambda v: v.astimezone(timezone(timedelta(hours=+8))).strftime('%Y-%m-%d %H:%M:%S')
        }


class PromptPage(BaseModel):
    total: int
    prompts: list[PromptVO]
