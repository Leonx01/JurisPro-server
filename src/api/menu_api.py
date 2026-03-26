from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from schemas.menu_schema import MenuCreate, MenuUpdate
from services.menu_service import MenuService
from src.services.sys_service import SysService
from src.utils.dependencies import get_db, get_current_user, get_redis
from src.utils.response import ResponseModel

router = APIRouter(prefix="/menus", tags=["Menus"])


@router.get("/all")
async def load_menus(db: Session = Depends(get_db)):
    routes = MenuService.load_menus(db)
    return ResponseModel.success(data=routes)


@router.get("/lazy")
async def lazy_load_menus(mid: int, db: Session = Depends(get_db)):
    """懒加载菜单"""
    menus = MenuService.lazy_load_menus(db, mid)
    return ResponseModel.success(data=menus)


@router.post("/menu")
async def add_menu(menu: MenuCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # SysService.add_menu(db, menu)
    menu.created_by = current_user['uname']
    menu.updated_by = current_user['uname']
    MenuService.add_menu(db, menu)
    return ResponseModel.success(message="Menu added successfully")


@router.put("/menu")
async def update_menu(menu: MenuUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # SysService.add_menu(db, menu)
    menu.updated_by = current_user['uname']
    MenuService.update_menu(db, menu)
    return ResponseModel.success(message="Menu added successfully")


@router.delete("/menu")
async def delete_menu(mid: int, db: Session = Depends(get_db)):
    MenuService.delete_menu(db, mid)
    return ResponseModel.success(message="Menu deleted successfully")
