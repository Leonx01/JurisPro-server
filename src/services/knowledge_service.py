from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.error_codes import ErrorCode
from exceptions.exception import AppException
from repositories.law_repository import LawRepository
from repositories.section_repository import SectionRepository
from schemas.law_schema import LawPage
from schemas.law_schema import LawUpdate
from schemas.section_schema import SectionPage
from services.llm_service import LLMService
from src.repositories.embedding_repository import EmbeddingRepository


class KnowledgeService:
    # Law Management
    @staticmethod
    def get_laws(es: Elasticsearch, keyword: str, status: str, page: int, pagesize: int) -> LawPage:
        try:

            page = LawRepository.get_laws(es, keyword, status, page, pagesize)
            return page
        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Database error: {str(e)}") from e

    @staticmethod
    def update_law(db: Session, law: LawUpdate):
        try:
            LawRepository.update_law(db, law)
        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Database error: {str(e)}") from e

    @staticmethod
    def get_sections(es: Elasticsearch, lid: int, keyword: str, page: int, pagesize: int):
        try:
            page = SectionRepository.get_sections(es, lid, keyword, page, pagesize)
            return page
        except Exception as e:
            raise AppException(ErrorCode.ELASTICSEARCH_ERROR, f"Elastic error:{str(e)}") from e

    @staticmethod
    def generate_embeddings(es: Elasticsearch, model: SentenceTransformer):
        index_name = "sections"
        EmbeddingRepository.generate_embeddings(es, model, index_name, "content")

    @staticmethod
    def retrieve(es: Elasticsearch, model: SentenceTransformer, query: str, strategy: str = "knn"):
        if strategy == "knn":
            return SectionRepository.retrieve_sections_knn(es, model, query)
        elif strategy == "bm25":
            pass
            # return SectionRepository.retrieve_sections_bm25(es, model, query)
        else:  # hybrid
            return SectionRepository.retrieve_sections_hybrid(es, model, query)

    @staticmethod
    def retrieve_page(redis,db: Session, es: Elasticsearch, model: SentenceTransformer, query: str, page: int,
                      page_size: int,
                      strategy: str = "knn", use_ai: bool = False) -> SectionPage:

        if use_ai:
            if not redis.get(query):
                re_query = LLMService.generate_response_by_code(db, code="rewrite", query=query)
                redis.setex(query, 3600, re_query)
                query = re_query
            else:
                query = redis.get(query)
        if strategy == "bm25":
            return SectionRepository.retrieve_sections_bm25_paginated(es, query, page, page_size)
        else:
            # strategy == "knn" or hybrid
            return SectionRepository.retrieve_sections_knn_paginated(es, model, query, page, page_size)
