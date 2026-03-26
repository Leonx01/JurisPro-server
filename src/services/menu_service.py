from sqlalchemy.orm import Session

from repositories.menu_repository import MenuRepository
from schemas.menu_schema import MenuUpdate, MenuCreate


class MenuService:
    @staticmethod
    def lazy_load_menus(db: Session, mid: int):
        return MenuRepository.lazy_load_menus(db, mid)

    @staticmethod
    def load_menus(db: Session):
        return MenuRepository.get_menus(db)

    @staticmethod
    def delete_menu(db: Session, mid: int):
        MenuRepository.delete_menu(db, mid)

    @staticmethod
    def add_menu(db: Session, menu: MenuCreate):
        MenuRepository.add_menu(db, menu)

    @staticmethod
    def update_menu(db: Session, menu: MenuUpdate):
        MenuRepository.update_menu(db, menu)
