from elasticsearch import Elasticsearch
from fastapi import APIRouter
from fastapi import Query
from fastapi.params import Depends
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from src.services.knowledge_service import KnowledgeService
from utils.dependencies import get_elastic, embed, get_db, get_redis
from utils.response import ResponseModel

router = APIRouter(prefix="/retrieve", tags=["Retrieve"])


@router.get("/laws")
async def retrieve_laws(
        redis=Depends(get_redis),
        db: Session = Depends(get_db),
        es_client: Elasticsearch = Depends(get_elastic), model: SentenceTransformer = Depends(embed),
        page: int = Query(1),
        page_size: int = Query(10),
        query: str = Query(None),
        strategy: str = Query(None),
        use_ai: bool = Query(False)):
    page = KnowledgeService.retrieve_page(redis,db, es_client, model, query, page, page_size, strategy, use_ai)
    return ResponseModel.success(data=page)
