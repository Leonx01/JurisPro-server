from typing import Optional

from pydantic import BaseModel, SecretStr


class GenerativeModelUpdate(BaseModel):
    id: int
    label: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None  # 可使用 Enum 进一步约束，比如 'I' 或 'E'
    api_key: Optional[str] = None
    provider: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None  # 可考虑 Enum: '0' or '1'
    updated_by: Optional[str] = None


class GenerativeModelCreate(BaseModel):
    label: str
    name: str
    type: str

    api_key: Optional[str] = None
    provider: Optional[str] = None

    description: Optional[str] = ''
    status: str  # 可考虑 Enum: '0' or '1'
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


from datetime import datetime, timezone, timedelta


class GenerativeModelAdminVO(BaseModel):
    id: int
    label: str
    name: str
    # avatar: Optional[str] = None
    type: str  # 可使用 Enum 进一步约束，比如 'I' 或 'E'

    api_key: Optional[str] = None
    # base_url: Optional[str] = None
    provider: Optional[str] = None

    description: Optional[str] = ''
    connection: str  # '0', '1', '2' 等
    status: str  # 可考虑 Enum: '0' or '1'

    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = 'system'
    updated_by: Optional[str] = 'system'

    class Config:
        from_attributes = True  # 允许从 ORM 模型转换
        json_encoders = {
            datetime: lambda v: v.astimezone(timezone(timedelta(hours=+8))).strftime('%Y-%m-%d %H:%M:%S')
        }  # 规范为 UTC-8 时间格式


class GenerativeModelConfig(BaseModel):
    id: int
    provider: str
    name: str
    api_key: Optional[SecretStr] = None  # api_key 可以为空

    # base_url: Optional[str] = None  # base_url 可以为空

    class Config:
        from_attributes = True  # 允许从 ORM 模型转换


class GenerativeModelUserVO(BaseModel):
    id: int
    label: str
    description: Optional[str] = None
    avatar: Optional[str] = None

    class Config:
        from_attributes = True  # 允许从 ORM 模型转换
