from typing import Dict, Optional

from pydantic import BaseModel


class Function(BaseModel):
    id: int
    name: str
    code: str

    class Config:
        from_attributes = True


class LLMFunctionMatrix(BaseModel):
    id: int
    label: str
    functions: Dict[str, bool]


class LLMFunctionMatrixUpdate(BaseModel):
    id: int
    functions: Dict[str, bool]


class FunctionCreate(BaseModel):
    name: str
    code: str
    created_by: Optional[str] = 'system'
    need_prompt: Optional[str] = '1'
    pid: Optional[int] = None


class FunctionVO(BaseModel):
    id: int
    name: str
    code: str
    need_prompt: str
    pid: Optional[int] = None
    children: Optional[list] = []
    slots: Optional[list[str]] = []
    prompt_id: Optional[int] = None

    class Config:
        from_attributes = True


class SetPromptRequest(BaseModel):
    fid: int
    pid: int
