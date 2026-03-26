from typing import List, Optional

from pydantic import BaseModel


class LawCreate(BaseModel):
    name: str
    version: str
    description: Optional[str] = None
    created_by: str
    status: str


from datetime import datetime, timezone, timedelta


class LawUpdate(BaseModel):
    id: int
    name: str
    version: str
    description: Optional[str] = None
    updated_by: Optional[str] = None
    status: str


class LawVO(BaseModel):
    id: int
    name: str
    version: str
    description: Optional[str] = None
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    status: str

    class Config:
        from_attributes = True  # 允许从 ORM 模型转换
        json_encoders = {
            datetime: lambda v: v.astimezone(timezone(timedelta(hours=+8))).strftime('%Y-%m-%d %H:%M:%S')
        }


class LawPage(BaseModel):
    total: int
    laws: List[LawVO]

