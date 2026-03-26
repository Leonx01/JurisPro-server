from fastapi import APIRouter
from fastapi import Depends
from requests import Session

from src.services.app_service import AppService
from src.utils.response import ResponseModel

router = APIRouter(prefix="/test", tags=["Test"])

from src.utils.dependencies import get_elastic, get_db


@router.get("/test")
async def get_test():
    # routes = AppService.get_routes(db)
    return ResponseModel.success()


@router.get("/routes")
def get_routes(db: Session = Depends(get_db)):
    routes = AppService.get_routes(db)
    return ResponseModel.success(data=routes)


@router.get("/elastic/ping")
def check_connection(es_client=Depends(get_elastic)):
    return es_client.ping()


@router.get("/elastic/info")
def get_info(es_client=Depends(get_elastic)):
    return es_client.info()


@router.post("/elastic/indices")
def create_index(index_name: str, es_client=Depends(get_elastic)):
    """创建索引，如果索引已存在则忽略"""
    if not es_client.indices.exists(index=index_name):
        es_client.indices.create(index=index_name)
        return ResponseModel.success(message=f"索引 {index_name} 创建成功")
    else:
        return ResponseModel.success(message=f"索引 {index_name} 已存在")

# @router.post("/elastic/insert")
# def insert_document(es=Depends(get_elastic)):
#     """插入文档到指定索引"""
#     try:
#         index_name = "law"
#
#         documents = [
#             {
#                 "name": "全国人民代表大会常务委员会关于惩治骗购外汇、逃汇和非法买卖外汇犯罪的决定",
#                 "version": "1998-12-29",
#                 "description": "该决定针对外汇管理领域违法犯罪行为制定的法律文件..."
#             },
#             {
#                 "name": "刑法",
#                 "version": "1997-10-01",  # 确保日期格式正确
#                 "description": "《中华人民共和国刑法》是为了惩罚犯罪，保护人民..."
#             },
#             {
#                 "name": "反电信网络诈骗法",
#                 "version": "2022-09-02",
#                 "description": "《中华人民共和国反电信网络诈骗法》是为了预防、遏制和惩治电信网络诈骗活动的专门法律..."
#             }
#         ]
#
#         # 遍历文档，使用 `update` + `doc_as_upsert`
#         for doc in documents:
#             doc_id = f"{doc['name']}_{doc['version']}"  # 生成唯一 ID
#             es.update(index=index_name, id=doc_id, body={"doc": doc, "doc_as_upsert": True})
#
#
#     except Exception as e:
#         raise AppException(ErrorCode.ELASTICSEARCH_ERROR)
#     # es.index(index=index_name, id=doc_id, document=document)
#     return ResponseModel.success(message="文档插入成功")
#
#
# @router.post("/llm/invoke")
# def invoke_llm(model_id: int, user_query: str, db: Session = Depends(get_db)):
#     # user_query = "I want to buy a car"
#     resp = LLMService.llm_invoke(user_query, model_id, db)
#     return ResponseModel.success(data=resp)
