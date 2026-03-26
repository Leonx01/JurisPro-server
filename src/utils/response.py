from typing import Generic, TypeVar, Optional

from pydantic import BaseModel

from src.exceptions.error_codes import ErrorCode  # 导入 ErrorCode

# 定义泛型
T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """ 统一 API 响应模型 """

    code: int  # 状态码
    message: str  # 提示信息
    data: Optional[T] = None  # 具体数据（可选）

    @staticmethod
    def success(data: Optional[T] = None, message: str = "Success") -> "ResponseModel[T]":
        """ 成功响应 """
        return ResponseModel(code=200, message=message, data=data)

    @staticmethod
    def error(error: ErrorCode) -> "ResponseModel":
        """ 失败响应，基于 ErrorCode """
        return ResponseModel(code=error.code, message=error.msg, data=None)
