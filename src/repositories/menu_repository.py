from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.error_codes import ErrorCode
from exceptions.exception import AppException
from models import Menu
from schemas.menu_schema import Route, Meta, MenuSchema, MenuCreate, MenuUpdate


class MenuRepository:

    @staticmethod
    def lazy_load_menus(db: Session, mid: int):
        """懒加载菜单"""
        # print("Loading menus with ID:", mid)
        db_menu = db.query(Menu).filter(Menu.mid == mid).first()
        if not db_menu:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND)
        # print("Loaded menu:", db_menu)
        return db_menu

    @staticmethod
    def delete_menu(db: Session, mid: int):
        """删除菜单"""
        # print("Deleting menu with ID:", mid)
        db_menu = db.query(Menu).filter(Menu.mid == mid).first()
        if not db_menu:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND)
        db_menu.del_flag = 1
        try:
            db.commit()
            db.refresh(db_menu)
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"{e}")

    @staticmethod
    def update_menu(db: Session, menu: MenuUpdate):
        db_menu = db.query(Menu).filter(Menu.mid == menu.mid).first()
        if not db_menu:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND)
        db_menu.updated_by = menu.updated_by
        db_menu.auth = menu.auth
        db_menu.icon = menu.icon
        db_menu.path = menu.path
        db_menu.component = menu.component
        db_menu.redirect = menu.redirect
        db_menu.order_num = menu.order_num
        db_menu.status = menu.status
        db_menu.title = menu.title
        db_menu.name = menu.name
        try:
            db.commit()
            db.refresh(db_menu)
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"数据库操作失败: {e}")

    @staticmethod
    def get_routes(db: Session) -> List[Route]:
        # 获取所有父级菜单（parent_id 为 None）
        menus = db.query(Menu).filter(Menu.del_flag == 0).filter(Menu.parent_id.is_(None)).filter(
            Menu.type != 'F').filter(Menu.status == '1').order_by(
            Menu.order_num).all()

        # 构建递归的 Route 数据
        def build_route(menu: Menu) -> Route:
            # 获取当前菜单的子菜单
            children_menus = db.query(Menu).filter(Menu.del_flag == 0).filter(Menu.parent_id == menu.mid).filter(
                Menu.status == '1').filter(Menu.type != 'F').order_by(Menu.order_num).all()

            # 创建一个 Route 对象
            route = Route(
                path=menu.path,
                component=menu.component,
                redirect=menu.redirect,
                name=menu.name,
                meta=Meta(
                    title=menu.title,
                    auth=menu.auth,
                    icon=menu.icon,
                    activeMenu=menu.active_menu,
                    menu=True if menu.menu == '1' else False,
                    breadcrumb=True if menu.breadcrumb == '1' else False
                ),
                children=[build_route(child) for child in children_menus] if children_menus else None
            )

            return route

        # 构建所有的父级菜单的 Route 对象
        routes: List[Route] = [build_route(menu) for menu in menus]

        return routes

    @staticmethod
    def get_menus(db: Session) -> List[MenuSchema]:
        # 获取所有父级菜单（parent_id 为 None）
        db_menus = db.query(Menu).filter(Menu.del_flag == 0).filter(Menu.parent_id.is_(None)).order_by(
            Menu.order_num).all()

        # 构建递归的 Menu 数据
        def build_menus(menu: Menu) -> MenuSchema:
            # 获取当前菜单的子菜单
            children_menus = db.query(Menu).filter(Menu.del_flag == 0).filter(Menu.parent_id == menu.mid).order_by(
                Menu.order_num).all()

            # 创建一个 Menu 对象
            menus_build = MenuSchema(
                mid=menu.mid,
                path=menu.path,
                component=menu.component,
                redirect=menu.redirect,
                order_num=menu.order_num,
                name=menu.name,
                title=menu.title,
                auth=menu.auth,
                icon=menu.icon,
                created_at=menu.created_at,
                created_by=menu.created_by,
                updated_at=menu.updated_at,
                updated_by=menu.updated_by,
                status=menu.status,
                type=menu.type,
                children=[build_menus(child) for child in children_menus] if children_menus else None
            )

            return menus_build

        # 构建所有的父级菜单的 Route 对象
        menus: List[MenuSchema] = [build_menus(db_menu) for db_menu in db_menus]

        return menus

    @staticmethod
    def add_menu(db: Session, menu: MenuCreate):
        db_menu = Menu(
            parent_id=menu.parent_id,
            title=menu.title,
            name=menu.name,
            component=menu.component,
            path=menu.path,
            type=menu.type,
            auth=menu.auth,
            icon=menu.icon,
            status=menu.status,
            order_num=menu.order_num,
            updated_by=menu.updated_by,
            created_by=menu.created_by,
            redirect=menu.redirect,
        )
        if menu.type == 'M':
            db_menu.breadcrumb = '1'
            db_menu.menu = '1'
        try:
            db.add(db_menu)
            db.flush()
            db.commit()
            db.refresh(db_menu)
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"数据库操作失败: {e}")
