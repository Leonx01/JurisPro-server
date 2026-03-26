import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.error_codes import ErrorCode
from exceptions.exception import AppException
from models import User, RoleMenus, Menu, Role
from schemas.role_schema import RoleVO
from schemas.user_schema import UserCreate, UserPage, UserAdminVO, UserUpdate, PasswordReset
from utils.generators import RandomSaltEncryptionUtil


class UserRepository:
    @staticmethod
    def get_all(db: Session) -> list[User]:
        """获取所有用户"""
        return db.query(User).filter(User.del_flag == 0).all()

    @staticmethod
    def reset_password(db: Session, user: PasswordReset) -> None:
        """重置用户密码"""
        user = db.query(User).filter(User.uid == user.uid).first()
        if not user:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND)
        user.password = RandomSaltEncryptionUtil.encypt(user.password)
        user.updated_by = user.updated_by
        try:
            db.commit()
            db.refresh(user)
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"数据库操作失败: {e}")

    @staticmethod
    def update_user(db: Session, user: UserUpdate):
        """更新用户信息"""
        db_user = db.query(User).filter(User.uid == user.uid).first()
        if not db_user:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND)
        if user.uname:
            db_user.uname = user.uname
            db_user.updated_by = user.updated_by
        if user.email:
            db_user.email = str(user.email)
            db_user.updated_by = user.updated_by
        if user.rid:
            db_user.rid = user.rid
            db_user.updated_by = user.updated_by
        if user.avatar:
            db_user.avatar = user.avatar
            db_user.updated_by = user.updated_by
        if user.status:
            db_user.status = user.status
            db_user.updated_by = user.updated_by
        try:
            db.commit()
            db.refresh(db_user)
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"数据库操作失败: {e}")

    @staticmethod
    def query_users(db: Session, page: int = 1, page_size: int = 10, keyword: str = None, status: str = None,
                    rid: int = None) -> UserPage:
        """查询用户"""
        query = db.query(User).filter(User.del_flag == 0)
        if keyword:
            query = query.filter(User.uname.like(f"%{keyword}%"))
        if status:
            query = query.filter(User.status == status)
        if rid:
            query = query.filter(User.rid == rid)
        total = query.count()
        db_users = query.offset((page - 1) * page_size).limit(page_size).all()
        users = []
        for db_user in db_users:
            db_role = db.query(Role).filter(Role.id == db_user.rid).first()
            role = RoleVO.model_validate(db_role) if db_role else None
            user = UserAdminVO(
                uid=db_user.uid,
                uname=db_user.uname,
                email=db_user.email,
                status=db_user.status,
                login_ip=db_user.login_ip,
                login_at=db_user.login_at,
                created_at=db_user.created_at,
                created_by=db_user.created_by,
                updated_at=db_user.updated_at,
                updated_by=db_user.updated_by,
                avatar=db_user.avatar,
                role=role,
            )
            users.append(user)
        user_page = UserPage(
            total=total,
            users=users, )
        return user_page

    @staticmethod
    def create(db: Session, user: UserCreate) -> User:
        new_user = User(
            uname=user.uname,
            email=user.email,
            password=RandomSaltEncryptionUtil.encypt(user.password),

            avatar=user.avatar,
            rid=user.rid,
            status=user.status,
            created_by=user.created_by,
            updated_by=user.updated_by,
        )
        try:
            db.add(new_user)
            db.flush()
            db.commit()
            db.refresh(new_user)
        except SQLAlchemyError as e:
            db.rollback()  # 发生错误时回滚事务
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"数据库操作失败: {e}")

        return new_user

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        user = db.query(User).filter(User.uid == user_id).first()
        if not user:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND)
        return user

    @staticmethod
    def delete(db: Session, user_id: int, updated_by: str) -> None:
        """删除用户"""
        db_user = db.query(User).filter(User.uid == user_id).first()
        db_user.del_flag = 1
        db_user.updated_by = updated_by
        try:
            db.commit()
            db.refresh(db_user)
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"数据库操作失败: {e}")

    @staticmethod
    def get_by_uname(db: Session, uname: str):
        user = db.query(User).filter(User.uname == uname).filter(User.del_flag == 0).filter(User.status == 1).first()
        return user

    @staticmethod
    def set_password(db: Session, user_id: int, password: str) -> User:
        user = db.query(User).filter(User.uid == user_id).first()
        user.password = password
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_login_info(db: Session, user_id: int, login_at: datetime, login_ip: str):
        user = db.query(User).filter(User.uid == user_id).first()
        user.login_at = login_at
        user.login_ip = login_ip
        db.commit()
        db.refresh(user)

    @staticmethod
    def get_permissions(db: Session, rid: int) -> list[str]:
        """
        根据角色ID获取该角色对应的权限标识符列表（auth 字段）
        :param db: 数据库会话对象
        :param rid: 角色ID
        :return: 权限标识符列表
        """
        permissions = (
            db.query(Menu.auth)
            .join(RoleMenus, RoleMenus.mid == Menu.mid)
            .filter(RoleMenus.rid == rid)
            .all()
        )
        # permissions 是一个 List[Tuple[str]]，提取非空的权限标识符
        return [auth for (auth,) in permissions if auth]