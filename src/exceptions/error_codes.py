from enum import Enum


class ErrorCode(Enum):
    """ 统一错误码管理（符合 HTTP 状态码规范） """

    # 400 系列：客户端错误
    BAD_REQUEST = (400, "请求格式错误")  # 泛指请求无效
    USER_NOT_FOUND = (404, "用户不存在")  # 404 更符合资源不存在的语义
    USER_ALREADY_EXISTS = (409, "用户已存在")  # 409 适用于资源冲突
    INVALID_PASSWORD = (401, "密码错误")  # 401 用于身份验证失败
    INVALID_EMAIL = (400, "无效的邮箱格式")
    INVALID_DATAFORMAT = (400, "数据格式错误")
    EMAIL_ALREADY_EXISTS = (409, "该邮箱已被注册")  # 409 适用于资源冲突
    INVALID_VERIFY_CODE = (400, "验证码错误或已失效")
    UNMOUNTED_DEPENDENCY = (400, "依赖未解除")
    INVALID_TOKEN = (401, "令牌无效")
    UNAUTHORIZED = (401, "未授权访问")  # 401 代表未认证
    FORBIDDEN = (403, "权限不足")  # 403 代表已认证但权限不足
    RESOURCE_NOT_FOUND = (404, "资源不存在")  # 资源不存在应使用 404
    LOGIN_ERROR = (404, "用户名或密码错误")  # 404 更符合资源不存在的语义
    MODEL_NOT_AVAILABLE = (404, "模型不可用")  # 404 更符合资源不存在的语义
    PROMPT_NOT_FOUND = (404, "提示词不存在")  # 404 更符合资源不存在的语义
    RESOURCE_ALREADY_EXISTS = (409, "资源已存在")  # 409 适用于资源冲突
    # 500 系列：服务器错误
    ELASTICSEARCH_ERROR = (500, "ES服务出错")
    SERVER_ERROR = (500, "服务器内部错误")
    DB_OPERATION_FAILED = (500, "数据库操作失败")
    MAIL_SEND_FAILED = (502, "邮件发送失败")  # 502 Bad Gateway 更符合外部服务失败
    UNKNOWN_ERROR = (500, "未知错误")
    REDIS_ERROR = (503, "缓存服务不可用")  # 503 代表服务不可用
    FILE_UPLOAD_FAIL = (500, "文件上传失败")

    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
