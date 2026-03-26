from sqlalchemy.orm import Session

from repositories.role_repository import RoleRepository
from schemas.role_schema import RoleVO, RoleMenuBind, RoleCreate, RoleUpdate, RolePage


class RoleService:
    @staticmethod
    def get_all_roles(db: Session) -> list[RoleVO]:
        """获取所有角色"""
        roles = RoleRepository.get_all(db)
        return roles

    @staticmethod
    def query_roles(db: Session, page: int, page_size: int, keyword: str, status: str) -> RolePage:
        """分页查询角色"""
        return RoleRepository.query_roles(db, page, page_size, keyword, status)

    @staticmethod
    def create_role(db: Session, role: RoleCreate):
        RoleRepository.create_role(db, role)

    @staticmethod
    def get_menus(db: Session, rid: int) -> RoleMenuBind:
        return RoleRepository.get_menus(db, rid)

    @staticmethod
    def update_menus(db: Session, menu_bind: RoleMenuBind):
        RoleRepository.update_menus(db, menu_bind)

    @staticmethod
    def delete_role(db: Session, rid: int):
        RoleRepository.delete_role(db, rid)

    @staticmethod
    def update_role(db: Session, role: RoleUpdate):
        RoleRepository.update_role(db, role)
