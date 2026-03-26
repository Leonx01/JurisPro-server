from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from schemas.role_schema import RoleMenuBind, RoleCreate, RoleUpdate
from services.role_service import RoleService
from src.utils.dependencies import get_db
from src.utils.response import ResponseModel
from utils.dependencies import get_current_user

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/")
async def get_all_roles(db: Session = Depends(get_db)):
    roles = RoleService.get_all_roles(db)
    return ResponseModel.success(data=roles)


@router.get("/role")
async def query_roles(db: Session = Depends(get_db),
                      keyword: str = Query(None),
                      status: str = Query(None),
                      page: int = Query(1),
                      page_size: int = Query(10)
                      ):
    roles = RoleService.query_roles(db, page, page_size, keyword, status)
    return ResponseModel.success(data=roles)


@router.post("/role")
async def create_role(role: RoleCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    role.created_by = current_user['uname']
    role.updated_by = current_user['uname']
    RoleService.create_role(db, role)
    return ResponseModel.success()


@router.put("/role")
async def update_role(role: RoleUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    role.updated_by = current_user['uname']
    RoleService.update_role(db, role)
    return ResponseModel.success()


@router.delete("/role")
async def update_role(rid: int, db: Session = Depends(get_db)):
    RoleService.delete_role(db, rid)
    return ResponseModel.success()


@router.get("/menus")
async def get_menus(rid: int, db: Session = Depends(get_db)):
    menus = RoleService.get_menus(db, rid)
    return ResponseModel.success(data=menus)


@router.put("/menus")
async def update_menus(menu_bind: RoleMenuBind, db: Session = Depends(get_db)):
    RoleService.update_menus(db, menu_bind)
    return ResponseModel.success()
