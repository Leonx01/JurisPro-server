from datetime import datetime, timezone, timedelta

from pydantic import BaseModel
from typing_extensions import Optional


class ChatCreate(BaseModel):
    uuid: str
    query: str
    model_id: int
    name: Optional[str] = None
    uid: Optional[int] = None


class ChatVO(BaseModel):
    id: int
    uuid: str
    name: Optional[str] = None
    uid: Optional[int] = None
    updated_at: datetime
    last_ai_msg: Optional[str] = None
    last_human_msg: Optional[str] = None

    class Config:
        from_attributes = True  # 允许从 ORM 模型转换
        json_encoders = {
            datetime: lambda v: v.astimezone(timezone(timedelta(hours=+8))).strftime('%Y-%m-%d %H:%M:%S')
        }


class ChatPage(BaseModel):
    total: int
    chats: list[ChatVO]
