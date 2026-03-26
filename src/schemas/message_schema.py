from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from schemas.law_schema import LawVO
from schemas.section_schema import SectionRetrieval


class UserMessageRaw(BaseModel):
    model_id: int
    query: str
    chat_uuid: str


class ChatHistory(BaseModel):
    role: str
    content: str

    def __str__(self) -> str:
        return f"{self.role.capitalize()}: {self.content}"


class UserQueryResponse(BaseModel):
    mid: int
    content: str
    docs: Optional[List[LawVO]] = None
    cases: Optional[List[LawVO]] = None
    created_at: datetime = None


class MessageCreate(BaseModel):
    type: Optional[str] = 'ai'
    content: str
    chat_uuid: str
    token_counts: Optional[int] = None
    model_id: Optional[int] = None
    response_time: Optional[float] = None
    created_at: datetime


class MessageVO(BaseModel):
    id: int
    type: Optional[str] = 'ai'
    content: str
    created_at: datetime
    token_counts: int
    model_id: Optional[int] = None
    response_time: Optional[float] = None
    related_laws: Optional[List[SectionRetrieval]] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }  # 规范为 UTC-8 时间格式


class MessagePage(BaseModel):
    offset: int
    messages: List[MessageVO]
