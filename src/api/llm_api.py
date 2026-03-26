from fastapi import APIRouter, Depends

from schemas.document_schema import DocumentCreate
from schemas.llm_schema import GenerativeModelCreate, GenerativeModelUpdate

router = APIRouter(prefix="/llm", tags=["LLM"])

from src.utils.dependencies import get_db, get_current_user
from src.services.llm_service import LLMService
from src.utils.response import ResponseModel
from src.schemas.message_schema import UserMessageRaw
from fastapi import Query


@router.get("/by-function")
async def get_model_by_function(function: str, db=Depends(get_db)):
    """ 根据功能获取模型列表 """
    models = LLMService.get_by_function(db, function)
    return ResponseModel.success(data=models)


@router.get("/models")
async def get_models(db=Depends(get_db), keyword: str = Query(None), type: str = Query(None),
                     status: str = Query(None)):
    """ 获取模型列表 """
    models = LLMService.query_llm(db, keyword, type, status)
    return ResponseModel.success(data=models)


@router.post("/model")
async def add_model(model: GenerativeModelCreate, db=Depends(get_db), user=Depends(get_current_user)):
    """ 添加模型 """
    model.created_by = user['uname']
    model.updated_by = user['uname']
    LLMService.add_llm(db, model)
    return ResponseModel.success(message="Model added successfully")


@router.delete("/model")
async def delete_model(mid: int = Query(None), db=Depends(get_db)):
    """ 删除模型 """
    LLMService.delete_llm(db, mid)
    return ResponseModel.success(message="Model deleted successfully")


@router.put("/model")
async def update_model(model: GenerativeModelUpdate, db=Depends(get_db), user=Depends(get_current_user)):
    """ 更新模型 """
    model.updated_by = user['uname']
    LLMService.update_llm(db, model)
    return ResponseModel.success(message="Model updated successfully")


@router.post("/generate")
async def generate_doc(request: DocumentCreate, db=Depends(get_db)):
    # response = LLMService.llm_invoke(request.query, request.model_id, db)
    # create doc
    # generate content
    return ResponseModel.success()


@router.post("/chat")
async def chat(request: UserMessageRaw, db=Depends(get_db)):
    # response = LLMService.llm_invoke(request.query, request.model_id, db)
    # return ResponseModel.success(data=response)
    pass


@router.get("/summarize")
async def summarize(query: str = Query(None), db=Depends(get_db)):
    """ 调用 LLM 进行推理 """
    resp = LLMService.generate_response_by_code(db, 'summary', query)
    return ResponseModel.success(data=resp)


@router.get("/suggest")
async def suggest(query: str = Query(None), db=Depends(get_db)):
    """ 调用 LLM 进行推理 """
    resp = LLMService.get_suggestions(db, query)
    # resp = LLMService.generate_response_by_code(db, 'suggest', query)
    return ResponseModel.success(data=resp)


@router.get("/rewrite")
async def rewrite(query: str = Query(None), db=Depends(get_db)):
    """ 调用 LLM 进行推理 """
    resp = LLMService.generate_response_by_code(db, 'rewrite', query)
    return ResponseModel.success(data=resp)


@router.get("/ping")
async def ping(mid: int = Query(None), db=Depends(get_db)):
    """ 测试 LLM 是否可用 """
    resp = LLMService.ping(db, mid)
    return ResponseModel.success(data=resp)
