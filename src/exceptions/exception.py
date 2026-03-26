from src.exceptions.error_codes import ErrorCode


class AppException(Exception):
    """ 业务异常类 """

    def __init__(self, error: ErrorCode, details: str = None):
        """
        :param error: 错误类型 (ErrorCode)
        :param details: 额外的错误详细信息
        """
        self.error = error
        self.code = error.code
        self.message = error.msg
        self.details = details  # 可以附加更多的详细信息

    def to_dict(self):
        """ 转换为字典格式 """
        error_info = {"code": self.code, "message": self.message}
        if self.details:
            error_info["details"] = self.details
        return error_info

    def __str__(self):
        """ 返回异常的字符串表示 """
        if self.details:
            return f"[{self.code}] {self.message}: {self.details}"
        return f"[{self.code}] {self.message}"

    def get_code(self):
        """ 获取错误代码 """
        return self.code
