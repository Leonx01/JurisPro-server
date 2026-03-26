import datetime
import random
import string
import uuid

import jwt
import hashlib

from src.configs import settings
from src.exceptions.error_codes import ErrorCode
from src.exceptions.exception import AppException


def generate_verification_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class IDGenerator(object):
    @classmethod
    def generate(cls) -> str:
        return uuid.uuid4().hex


class RandomSaltEncryptionUtil(object):
    @classmethod
    def encrypt_with_salt(cls, password: str, salt: str) -> str:
        encrypted_password = hashlib.md5((password + salt).encode()).hexdigest()
        return encrypted_password

    @classmethod
    def encypt(cls, password: str) -> str:
        salt = uuid.UUID(int=random.getrandbits(128)).hex
        # use MD5 to encrypt password
        db_password = f"{salt}${cls.encrypt_with_salt(password, salt)}"
        return db_password

    @classmethod
    def verify(cls, db_password: str, password: str) -> bool:
        salt, encrypt_password = db_password.split("$")
        input_password = cls.encrypt_with_salt(password, salt)
        return encrypt_password == input_password


class JwtToken(object):
    @classmethod
    def generate_token(cls, payload: dict, expires_in: int = None) -> str:
        if expires_in is None:
            expires_in = settings.jwt.expires_in
        headers = dict(typ="jwt", alg="HS256")
        # 计算过期时间
        exp_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
        payload.update({"exp": exp_time})  # 加入过期时间
        result = jwt.encode(
            payload=payload,
            key=settings.jwt.secret_key.get_secret_value(),
            algorithm="HS256",
            headers=headers
        )
        return result

    @classmethod
    def validate_and_parse(cls, token: str) -> dict:
        try:
            payload_data = jwt.decode(
                token,
                settings.jwt.secret_key.get_secret_value(),
                algorithms=['HS256']
            )
            return payload_data
        except jwt.ExpiredSignatureError as err:
            raise AppException(ErrorCode.INVALID_TOKEN, details=f"Token Expired:{err}") from err
        except jwt.InvalidTokenError as err:
            raise AppException(ErrorCode.INVALID_TOKEN, details=f"Invalid Token:{err}") from err
        except Exception as err:
            raise AppException(ErrorCode.UNKNOWN_ERROR, details=f"Unknown Error:{err}") from err


if __name__ == '__main__':
    # print(RandomSaltEncryptionUtil.encypt("123456"))
    print(
        RandomSaltEncryptionUtil.verify("bc2dcc96c2325ecaba3ee98fe64dac22$ec9413d09ef9257598556bf96f90ad40", "123456"))
