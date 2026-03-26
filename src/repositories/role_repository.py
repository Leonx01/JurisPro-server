from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.error_codes import ErrorCode
from exceptions.exception import AppException
from models import Role, RoleMenus
from schemas.role_schema import RoleVO, RoleMenuBind, RoleCreate, RoleUpdate, RolePage


class RoleRepository:
    @staticmethod
    def get_by_id(db: Session, rid: int) -> Role:
        """根据 ID 获取角色"""
        db_role = db.query(Role).filter(Role.id == rid).first()
        if not db_role:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND)
        return db_role

    @staticmethod
    def delete_role(db: Session, rid: int):
        try:
            db_role = db.query(Role).filter(Role.id == rid).first()
            if not db_role:
                raise AppException(ErrorCode.RESOURCE_NOT_FOUND)

            db_role.del_flag = 1

            db.commit()
            db.refresh(db_role)

        except AppException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"数据库更新失败: {e}")

    @staticmethod
    def get_all(db: Session) -> list[RoleVO]:
        db_roles = db.query(Role).filter(Role.del_flag == 0).all()
        roles = [RoleVO.model_validate(db_role) for db_role in db_roles]
        return roles

    @staticmethod
    def query_roles(db: Session, page: int, page_size: int, keyword: str, status: str) -> RolePage:
        db_roles = db.query(Role).filter(Role.del_flag == 0)
        if keyword:
            db_roles = db_roles.filter(Role.description.like(f"%{keyword}%"))
        if status:
            db_roles = db_roles.filter(Role.status == status)
        db_roles = db_roles.offset((page - 1) * page_size).limit(page_size).all()
        roles = [RoleVO.model_validate(db_role) for db_role in db_roles]
        total = db.query(Role).filter(Role.del_flag == 0).count()
        page = RolePage(
            total=total,
            roles=roles,
        )
        return page

    @staticmethod
    def update_role(db: Session, role: RoleUpdate):
        try:
            db_role = db.query(Role).filter(Role.id == role.id).first()
            if not db_role:
                raise AppException(ErrorCode.RESOURCE_NOT_FOUND)

            db_role.updated_by = role.updated_by
            db_role.status = role.status
            db_role.description = role.description
            db_role.name = role.name

            db.commit()
            db.refresh(db_role)

        except AppException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"数据库更新失败: {e}")

    @staticmethod
    def create_role(db: Session, role: RoleCreate):
        try:
            # 可选：检查是否已存在相同名称的角色
            existing = db.query(Role).filter(Role.name == role.name).first()
            if existing:
                raise AppException(ErrorCode.RESOURCE_ALREADY_EXISTS)

            # 创建角色对象
            db_role = Role(
                status=role.status,
                name=role.name,
                description=role.description,
                updated_by=role.updated_by,
                created_by=role.created_by
            )

            # 添加并提交
            db.add(db_role)
            db.commit()
            db.refresh(db_role)  # 获取插入后的 ID 等字段
        except AppException as e:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"{e}")

    @staticmethod
    def get_menus(db: Session, rid: int) -> RoleMenuBind:
        db_menus = db.query(RoleMenus).filter(RoleMenus.rid == rid).all()
        mid_list = [menu.mid for menu in db_menus]
        return RoleMenuBind(
            rid=rid,
            menus=mid_list
        )

    @staticmethod
    def update_menus(db: Session, menu_bind: RoleMenuBind):
        try:
            # 1. 删除旧记录
            db.query(RoleMenus).filter(RoleMenus.rid == menu_bind.rid).delete(synchronize_session=False)

            # 2. 构造批量插入对象
            new_menu_ids = set(menu_bind.menus)
            new_relations = [RoleMenus(rid=menu_bind.rid, mid=mid) for mid in new_menu_ids]

            # 3. 批量添加（比逐个 add 更高效）
            db.bulk_save_objects(new_relations)

            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"{e}")
