from fastapi import APIRouter, Depends

from schemas.function_schema import LLMFunctionMatrixUpdate, SetPromptRequest

router = APIRouter(prefix="/functions", tags=["Functions"])

from src.utils.dependencies import get_db
from src.services.function_service import FunctionService
from src.utils.response import ResponseModel


@router.get("/all")
async def get_functions(db=Depends(get_db)):
    """ 获取功能列表 """
    functions = FunctionService.get_all_functions(db)
    return ResponseModel.success(data=functions)


@router.get("/")
async def get_functions_by_id(fid: int, db=Depends(get_db)):
    """ 根据功能ID获取功能信息 """
    function = FunctionService.get_function_by_id(db, fid)
    return ResponseModel.success(data=function)


# @router.get("/")
# async def get_functions(db=Depends(get_db)):
#     """ 获取功能列表 """
#     functions = LLMService.get_functions(db)
#     return ResponseModel.success(data=functions)


@router.get("/matrix")
async def get_function_matrix(db=Depends(get_db)):
    """ 获取功能矩阵 """
    function_matrix = FunctionService.get_function_matrix(db)
    return ResponseModel.success(data=function_matrix)


@router.post("/matrix")
async def update_function_matrix(update: LLMFunctionMatrixUpdate, db=Depends(get_db)):
    """ 更新功能矩阵 """
    FunctionService.update_function_matrix(db, update)
    return ResponseModel.success()


@router.put("/prompt")
async def set_prompt(req: SetPromptRequest, db=Depends(get_db)):
    """ 更新功能矩阵 """
    FunctionService.set_prompt(db, req.fid, req.pid)
    return ResponseModel.success()
