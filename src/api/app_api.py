from fastapi import APIRouter

router = APIRouter(prefix="/app", tags=["Application"])

from src.utils.response import ResponseModel
from src.services.app_service import AppService
from src.utils.dependencies import get_db
from sqlalchemy.orm import Session
from fastapi import Depends


@router.get("/routes")
async def get_routes(db: Session = Depends(get_db)):
    routes = AppService.get_routes(db)
    return ResponseModel.success(data=routes)


@router.get("/dicts")
async def get_dicts(db: Session = Depends(get_db)):
    pass
