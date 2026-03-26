from fastapi import APIRouter, File, Depends, UploadFile,Query
from sqlalchemy.orm import Session

from src.services.sys_service import SysService
from src.utils.dependencies import get_db
from src.utils.response import ResponseModel

router = APIRouter(prefix="/sys", tags=["System"])


@router.get("/menus")
async def get_routes(db: Session = Depends(get_db)):
    routes = SysService.get_menus(db)
    return ResponseModel.success(data=routes)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), target_dir: str = Query(...)):
    # 获取扩展名，生成新文件名
    url = await SysService.save_file(file, target_dir)
    return ResponseModel.success(data=url)
