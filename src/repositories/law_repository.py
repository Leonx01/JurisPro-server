from elasticsearch import Elasticsearch
from sqlalchemy.orm import Session

from exceptions.error_codes import ErrorCode
from exceptions.exception import AppException
from models import Law
from schemas.law_schema import LawPage, LawVO, LawUpdate


class LawRepository:
    @staticmethod
    def get_laws(es: Elasticsearch, keyword: str, status: str, page: int, pagesize: int) -> LawPage | None:
        # 如果 keyword 为空，使用 match_all 查询
        if not keyword and not status:
            query = {
                "query": {
                    "match_all": {}  # 查询所有文档
                },
                "from": (page - 1) * pagesize,  # 起始页计算，page 从 1 开始
                "size": pagesize,  # 每页返回的记录数
                "track_total_hits": True  # 确保 Elasticsearch 返回 total count
            }
        else:
            # 构造 bool 查询，组合关键词搜索和状态筛选
            query = {
                "query": {
                    "bool": {
                        "must": [],  # 必须匹配的条件
                    }
                },
                "from": (page - 1) * pagesize,
                "size": pagesize,
                "track_total_hits": True  # 确保 Elasticsearch 返回 total count
            }

            # 如果有关键词，添加 multi_match 查询
            if keyword:
                query["query"]["bool"]["must"].append({
                    "multi_match": {
                        "query": keyword,
                        "fields": ["content", "name"]
                    }
                })

            # 如果有状态，添加 match 查询
            if status:
                query["query"]["bool"]["must"].append({
                    "match": {
                        "status": status
                    }
                })

        try:
            # 执行查询
            response = es.search(index="laws", body=query)
            # 解析结果，返回文档内容
        except Exception as e:
            raise AppException(ErrorCode.ELASTICSEARCH_ERROR, f"ES 查询失败: {str(e)}") from e

        laws = []
        try:
            for hit in response['hits']['hits']:
                law = LawVO(**hit['_source'])
                laws.append(law.model_dump())
            page = LawPage(total=response['hits']['total']['value'], laws=laws)
            return page
        except Exception as e:
            raise e

    @staticmethod
    def update_law(db: Session, law: LawUpdate):
        db_law = db.query(Law).filter(Law.id == law.id).first()
        if not db_law:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"未找到法律 ID={law.id}")
        db_law.name = law.name
        db_law.version = law.version
        db_law.status = law.status
        db_law.description = law.description
        db_law.updated_by = law.updated_by
        try:
            db.commit()
            db.refresh(db_law)
        except Exception as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"更新法律失败: {str(e)}") from e
