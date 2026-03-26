from pathlib import Path

from fastapi_mail import FastMail, MessageSchema
from jinja2 import Template
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.configs import settings
from src.exceptions.error_codes import ErrorCode
from src.exceptions.exception import AppException
from src.repositories.user_repository import UserRepository
from src.schemas.email_schema import EmailResetRequest
from src.schemas.user_schema import (
    UserRegister,
    UserCreate,
    UserLoginResponse,
    UserReset, UserLoginDTO,
)
from src.utils.generators import RandomSaltEncryptionUtil, generate_verification_code, JwtToken


class AuthService:

    @staticmethod
    async def send_verification_email(mail_client: FastMail, email: str) -> str:
        """ 发送邮箱验证码 """
        verify_code = generate_verification_code()

        template_path = Path(settings.mail.template_path) / "email.html"
        with open(template_path, "r", encoding="utf-8") as file:
            template = Template(file.read())

        html_content = template.render(verify_code=verify_code)

        message = MessageSchema(
            subject="邮箱验证",
            recipients=[email],
            body=html_content,
            subtype="html",
        )
        try:
            await mail_client.send_message(message)
        except Exception as e:
            raise AppException(ErrorCode.MAIL_SEND_FAILED, f"Mail Service error: {str(e)}") from e

        return verify_code  # 返回验证码，供 Redis 存储

    @staticmethod
    def register(db: Session, user: UserRegister) -> None:
        """ 注册新用户 """
        try:
            # 检查用户名是否已存在
            existing_user = UserRepository.get_by_uname(db, user.uname)
            if existing_user:
                raise AppException(ErrorCode.USER_ALREADY_EXISTS)

            # 创建用户对象
            user_create = UserCreate(
                uname=user.uname,
                email=user.email,
                password=user.password,
            )

            # 保存新用户到数据库
            new_user = UserRepository.create(db, user_create)
        except AppException as e:
            # 将检测出的AppException继续抛出
            raise e
        except SQLAlchemyError as e:
            # 捕获数据库操作相关的异常并附加详细信息
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Database error: {str(e)}") from e
        except Exception as e:
            # 捕获其他所有异常
            print(f"Unexpected error: {str(e)}")
            raise e

    @staticmethod
    def login(db: Session, user: UserLoginDTO) -> UserLoginResponse:
        """ 登录 """
        try:
            db_user = UserRepository.get_by_uname(db, user.uname)
            if not db_user or not RandomSaltEncryptionUtil.verify(db_user.password, user.password.get_secret_value()):
                raise AppException(ErrorCode.LOGIN_ERROR)
            # UPDATE LOGIN INFO
            UserRepository.update_login_info(db, db_user.uid, user.login_at, user.login_ip)

            return UserLoginResponse(
                uname=db_user.uname,
                avatar=db_user.avatar,
                token=JwtToken.generate_token({"uname": db_user.uname,"uid":db_user.uid,"role": db_user.rid}),
            )

        except SQLAlchemyError as e:
            # 处理数据库异常，防止影响业务逻辑
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Database error: {str(e)}") from e

        except AppException:
            # 业务异常不做二次封装，直接抛出
            raise

        except Exception as e:
            # 捕获其他未知异常，防止系统崩溃
            raise AppException(ErrorCode.UNKNOWN_ERROR, f"Unexpected error: {str(e)}") from e

    @staticmethod
    def validate_uname_email(db: Session, request: EmailResetRequest) -> None:
        """ 验证用户邮箱 """
        user = UserRepository.get_by_uname(db, request.uname)
        if not user:
            raise AppException(ErrorCode.USER_NOT_FOUND)
        if user.email != request.email:
            raise AppException(ErrorCode.EMAIL_NOT_MATCH)

    @staticmethod
    def reset_password(db: Session, user: UserReset) -> None:
        """ 重置密码 """
        try:
            # 尝试从数据库获取用户
            db_user = UserRepository.get_by_uname(db, user.uname)
            if not db_user:
                raise AppException(ErrorCode.USER_NOT_FOUND)

            # 加密密码
            db_user.password = RandomSaltEncryptionUtil.encypt(user.password)

            # 更新密码
            UserRepository.set_password(db, db_user.uid, db_user.password)

        except AppException as e:
            # 如果是业务逻辑异常，直接抛出
            raise e
        except SQLAlchemyError as e:
            # 捕获数据库操作相关的异常并附加详细信息
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Database error: {str(e)}") from e
        except Exception as e:
            # 捕获其他意外异常
            raise AppException(ErrorCode.INTERNAL_SERVER_ERROR, f"Unexpected error: {str(e)}") from e
