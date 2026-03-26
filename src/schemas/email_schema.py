from pydantic import BaseModel, EmailStr


class EmailRequest(BaseModel):
    email: EmailStr  # 确保输入是有效的邮箱地址


class EmailResetRequest(BaseModel):
    uname: str
    email: EmailStr  # 确保输入是有效的邮箱地址
