from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from schemas.user_schema import UserUpdate, PasswordReset, UserCreate
from src.services.user_service import UserService
from src.utils.dependencies import get_db, get_current_user
from src.utils.response import ResponseModel

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/permission")
async def get_permission(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    role = current_user.get("role")
    permissions = UserService.get_permissions(db, role)
    return ResponseModel.success(data=permissions)


from fastapi import Query


@router.get("/")
async def query_users(db: Session = Depends(get_db),
                      keyword: str = Query(None),
                      status: str = Query(None),
                      rid: int = Query(None),
                      page: int = Query(1),
                      page_size: int = Query(10)
                      ):
    users = UserService.query_users(db, page, page_size, keyword, status, rid)
    return ResponseModel.success(data=users)


@router.put("/user")
async def update_user(user: UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """更新用户信息"""
    user.updated_by = current_user['uname']
    UserService.update_user(db, user)
    return ResponseModel.success()


@router.get("/reset/password")
async def reset_password(uid: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """重置用户密码"""
    password = "123456"
    user = PasswordReset(uid=uid, password=password, updated_by=current_user['uname'])
    UserService.reset_password(db, user)
    return ResponseModel.success()


@router.delete("/user")
async def delete_user(uid: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """删除用户"""
    uname = current_user['uname']
    UserService.delete_user(db, uid, uname)
    return ResponseModel.success()


@router.post("/user")
async def create_user(user: UserCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """ 注册新用户 """
    user.created_by = current_user['uname']
    user.updated_by = current_user['uname']
    user.password = "123456"
    UserService.create_user(db, user)
    return ResponseModel.success(message="创建成功")


@router.get("/info")
async def get_userinfo(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """获取用户信息"""
    user = UserService.get_userinfo(db, current_user['uid'], current_user['role'])
    return ResponseModel.success(data=user)


@router.put("/info")
async def update_userinfo(user: UserUpdate, db: Session = Depends(get_db),
                          current_user=Depends(get_current_user)):
    """获取用户信息"""
    user.updated_by = current_user['uname']
    user.uid = current_user['uid']
    UserService.update_user(db, user)
    return ResponseModel.success()
