from datetime import datetime, timezone, timedelta
from typing import List, Optional

from pydantic import BaseModel


class SectionVO(BaseModel):
    id: int
    law: str
    no: str
    content: str
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    content_highlight: Optional[str] = None

    class Config:
        from_attributes = True  # 允许从 ORM 模型转换
        json_encoders = {
            datetime: lambda v: v.astimezone(timezone(timedelta(hours=+8))).strftime('%Y-%m-%d %H:%M:%S')
        }


class SectionPage(BaseModel):
    total: int
    sections: List[SectionVO]


class SectionRetrieval(BaseModel):
    id: int
    law: str
    no: str
    content: str

    def __str__(self) -> str:
        return f"《{self.law}》 {self.no} {self.content}"
