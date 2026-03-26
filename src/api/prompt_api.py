from fastapi import APIRouter, Depends, Query

from schemas.prompt_schema import PromptCreate, PromptUpdate
from services.prompt_service import PromptService

router = APIRouter(prefix="/prompt", tags=["Prompt"])
from src.utils.dependencies import get_db, get_current_user
from src.utils.response import ResponseModel


@router.post("")
async def add_prompt(prompt: PromptCreate, db=Depends(get_db), user=Depends(get_current_user)):
    prompt.created_by = user['uname']
    prompt.updated_by = user['uname']
    PromptService.add_prompt(db, prompt)
    return ResponseModel.success()


@router.get("/all")
async def get_all_prompts(db=Depends(get_db)):
    prompts = PromptService.get_all_prompts(db)
    return ResponseModel.success(data=prompts)


@router.get("/query")
async def get_prompts(keyword: str = Query(None), fid: int = Query(None), db=Depends(get_db)):
    prompts = PromptService.get_prompts(db, keyword, fid)
    return ResponseModel.success(data=prompts)


@router.get("/page")
async def get_prompts(keyword: str = Query(None), fid: int = Query(None), page: int = Query(1),
                      page_size: int = Query(10), db=Depends(get_db)):
    prompts = PromptService.get_prompt_page(db, keyword, fid, page, page_size)
    return ResponseModel.success(data=prompts)


@router.get("")
async def get_prompt_by_id(pid: int, db=Depends(get_db)):
    prompt = PromptService.get_prompt_by_id(db, pid)
    return ResponseModel.success(data=prompt)


@router.put("")
async def update_prompts(prompt: PromptUpdate, user=Depends(get_current_user), db=Depends(get_db)):
    prompt.updated_by = user["uname"]
    PromptService.update_prompt(db, prompt)
    return ResponseModel.success()


@router.delete("")
async def delete_prompt(pid: int, db=Depends(get_db)):
    PromptService.delete_prompt(db, pid)
    return ResponseModel.success()
