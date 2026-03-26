import datetime
import time

import redis
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from src.exceptions.error_codes import ErrorCode
from src.exceptions.exception import AppException
from src.schemas.email_schema import EmailRequest, EmailResetRequest
from src.schemas.user_schema import UserLogin, UserResetVerify, UserReset, UserRegister, UserLoginDTO
from src.services.auth_service import AuthService
from src.utils.dependencies import get_db, get_smtp, get_redis
from src.utils.response import ResponseModel

router = APIRouter(prefix="/auth", tags=["Authentications"])


# 公共函数：验证验证码
def validate_verify_code(redis_client: redis.Redis, email: str, verify_code: str):
    """ 验证验证码是否有效 """
    cached_code = redis_client.get(email)
    if not cached_code or cached_code != verify_code:
        raise AppException(ErrorCode.INVALID_VERIFY_CODE)


@router.post("/login")
async def login(user: UserLogin, request: Request, db: Session = Depends(get_db)):
    login_ip = request.client.host
    login_at = datetime.datetime.now()
    user_login_dto = UserLoginDTO(
        uname=user.uname,
        password=user.password,
        login_ip=login_ip,
        login_at=login_at
    )
    user_store = AuthService.login(db, user_login_dto)
    user_store.avatar = f'http://localhost:8000{user_store.avatar}'
    return ResponseModel.success(message="登陆成功", data=user_store)


@router.post("/logout")
async def logout():
    return ResponseModel.success(message="登出成功")


@router.post("/reset")
async def reset_password(request: UserReset, db: Session = Depends(get_db)):
    """ 重置密码 """
    AuthService.reset_password(db, request)
    return ResponseModel.success(message="密码重置成功")


@router.post("/reset/validate")
async def validate_reset_verifycode(request: UserResetVerify, redis_client=Depends(get_redis)):
    """ 验证重置密码验证码 """
    validate_verify_code(redis_client, str(request.email), request.verifyCode)
    # 如果验证失败，则会抛出错误
    return ResponseModel.success(message="验证成功")


@router.post("/reset/email")
async def send_reset_email(request: EmailResetRequest, redis_client=Depends(get_redis), db: Session = Depends(get_db),
                           mail_client=Depends(get_smtp)):
    """ 发送重置密码邮件 """
    AuthService.validate_uname_email(db, request)
    verification_code = await AuthService.send_verification_email(mail_client, str(request.email))

    # 设置验证码到Redis
    try:
        redis_client.setex(request.email, 300, verification_code)
    except Exception as e:
        raise AppException(ErrorCode.REDIS_ERROR, f"Redis Cache error: {str(e)}") from e

    return ResponseModel.success(message="邮件发送成功")


@router.post("/register")
async def register(user: UserRegister, db: Session = Depends(get_db), redis_client=Depends(get_redis)):
    """ 注册新用户 """
    validate_verify_code(redis_client, str(user.email), user.verifyCode)  # 验证验证码
    AuthService.register(db, user)
    return ResponseModel.success(message="注册成功")


@router.post("/register/email")
async def send_verification_email(request: EmailRequest, redis_client=Depends(get_redis),
                                  mail_client=Depends(get_smtp)):
    """ 发送验证码邮件 """
    verification_code = await AuthService.send_verification_email(mail_client, str(request.email))
    redis_client.setex(request.email, 300, verification_code)  # 设置 key，300 秒后过期
    return ResponseModel.success(message="邮件发送成功")
