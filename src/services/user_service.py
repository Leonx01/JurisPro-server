from sqlalchemy.orm import Session

from repositories.role_repository import RoleRepository
from schemas.user_schema import UserUpdate, PasswordReset, UserInfoVO, UserInfoUpdate
from src.exceptions.exception import AppException
from src.repositories.user_repository import UserRepository
from src.schemas.user_schema import UserCreate, UserResponse, UserPage


class UserService:
    @staticmethod
    def get_userinfo(db: Session, uid: int, rid: int) -> UserInfoVO:
        """根据用户ID获取用户信息"""
        user = UserRepository.get_by_id(db, uid)
        role = RoleRepository.get_by_id(db, rid)
        userinfo = UserInfoVO(
            uid=user.uid,
            uname=user.uname,
            email=user.email,
            avatar=user.avatar,
            created_at=user.created_at,
            login_at=user.login_at,
            role=role.description,
        )
        return userinfo

    @staticmethod
    def query_users(db: Session, page: int, page_size: int, keyword: str, status: str, rid: int) -> UserPage:
        """根据关键字查询用户列表"""
        user_page = UserRepository.query_users(db, page, page_size, keyword, status, rid)
        return user_page

    @staticmethod
    def reset_password(db: Session, user: PasswordReset) -> None:
        """重置用户密码"""
        UserRepository.reset_password(db, user)

    @staticmethod
    def update_user(db: Session, user: UserUpdate):
        """更新用户信息"""
        UserRepository.update_user(db, user)

    @staticmethod
    def get_all_users(db: Session,

                      ) -> list[UserResponse]:
        users = UserRepository.get_all(db)
        return [UserResponse.model_validate(user) for user in users]

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> UserResponse:
        new_user = UserRepository.create(db, user)
        return UserResponse.model_validate(new_user)

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> UserResponse | None:
        user = UserRepository.get_by_id(db, user_id)
        return UserResponse.model_validate(user) if user else None

    # @staticmethod
    # def update_user(db: Session, user_id: int, user_data: UserCreate) -> UserResponse | None:
    #     updated_user = UserRepository.update(db, user_id, user_data)
    #     return UserResponse.model_validate(updated_user) if updated_user else None

    @staticmethod
    def delete_user(db: Session, user_id: int, updated_by: str) -> None:
        UserRepository.delete(db, user_id, updated_by)

    @staticmethod
    def get_permissions(db: Session, role: int) -> list[str]:
        try:
            permissions = UserRepository.get_permissions(db, role)
            return permissions
        except AppException as err:
            raise err
