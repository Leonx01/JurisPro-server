from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from schemas.document_schema import DocTypeCreate, DocTypeUpdate
from schemas.law_schema import LawUpdate
from services.knowledge_service import KnowledgeService
from src.utils.dependencies import get_db, get_current_user
from src.utils.dependencies import get_elastic
from utils.dependencies import embed
from utils.response import ResponseModel

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


@router.get("/laws")
async def get_laws(es_client=Depends(get_elastic), keyword: str = Query(None), status: str = Query(None),
                   page: int = Query(1), page_size: int = Query(10)):
    page = KnowledgeService.get_laws(es_client, keyword, status, page, page_size)
    return ResponseModel.success(data=page)


@router.put("/law")
async def update_law(law: LawUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """ 更新法律 """
    law.updated_by = current_user['uname']
    law = KnowledgeService.update_law(db, law)
    return ResponseModel.success(data=law)


@router.get("/sections")
async def get_sections(lid: int, keyword: str = Query(None),
                       page: int = Query(1), page_size: int = Query(10), es_client=Depends(get_elastic), ):
    page = KnowledgeService.get_sections(es_client, lid, keyword, page, page_size)
    return ResponseModel.success(data=page)


@router.get("/generate_embeddings")
async def generate_embeddings(es_client=Depends(get_elastic), model=Depends(embed)):
    KnowledgeService.generate_embeddings(es_client, model)
    return ResponseModel.success(message="Embeddings generated successfully")


@router.get("/retrieve")
async def retrieve(query: str, strategy: str = "knn", es_client=Depends(get_elastic), model=Depends(embed)):
    results = KnowledgeService.retrieve(es_client, model, query, strategy)
    return ResponseModel.success(data=results)


# @router.get("/doc-types")
# async def get_doc_types(db: Session = Depends(get_db), keyword: str = Query(None), status: str = Query(None)):
#     types = KnowledgeService.get_doc_types(db, keyword, status)
#     return ResponseModel.success(data=types)
#
#
# @router.post("/doc-type")
# async def add_doc_type(doc: DocTypeCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
#     doc.created_by = user['uname']
#     doc.updated_by = user['uname']
#     KnowledgeService.add_doc_type(db, doc)
#     return ResponseModel.success()
#
#
# @router.put("/doc-type")
# async def update_doc_type(doc: DocTypeUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
#     doc.updated_by = user['uname']
#     KnowledgeService.update_doc_type(db, doc)
#     return ResponseModel.success()
#
#
# @router.delete("/doc-type")
# async def delete_doc_type(id: int, db: Session = Depends(get_db)):
#     KnowledgeService.delete_doc_type(db, id)
#     return ResponseModel.success()
