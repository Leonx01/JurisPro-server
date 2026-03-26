from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models import LLMFunction, DocType
from exceptions.error_codes import ErrorCode
from exceptions.exception import AppException
from schemas.document_schema import DocTypeCreate, DocTypeUpdate, DocTypeVO


class DocTypeRepository:
    @staticmethod
    def get_doc_type_by_id(db: Session, doc_id: int) -> DocType:
        """根据ID获取文档类型"""
        db_doc_type = db.query(DocType).filter(DocType.id == doc_id).first()
        if not db_doc_type:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"DocType[ID:{doc_id}] Not Found")
        return db_doc_type

    @staticmethod
    def delete_doc_type(db: Session, doc_id: int):
        db_doc_type = db.query(DocType).filter(DocType.id == doc_id).first()
        fid = db_doc_type.fid if db_doc_type else None
        if fid:
            function = db.query(LLMFunction).filter(LLMFunction.id == fid).first()
            if function:
                try:
                    db.delete(function)
                    db.commit()
                except SQLAlchemyError as e:
                    db.rollback()
                    raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Failed to delete Function: {str(e)}") from e
        # 删除文档类型
        if not db_doc_type:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"DocType[ID:{doc_id}] Not Found")
        try:
            db.delete(db_doc_type)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Failed to delete DocType: {str(e)}") from e

    @staticmethod
    def get_available_doc_types(db: Session) -> List[DocType]:
        """获取所有文档类型"""
        # status == 1
        types = db.query(DocType).filter(DocType.status == '1').all()
        # binding function has prompt
        result = []
        for doc_type in types:
            function = db.query(LLMFunction).filter(LLMFunction.id == doc_type.fid).first()
            if function.prompt_id:
                result.append(doc_type)
        return result

    @staticmethod
    def get_doc_types(db: Session, keyword: str, status: str) -> List[DocTypeVO]:
        query = db.query(DocType)
        if keyword:
            query = query.filter(DocType.label.contains(keyword))
        if status:
            query = query.filter(DocType.status == status)
        types = query.all()
        return [DocTypeVO.model_validate(doc_type) for doc_type in types]

    @staticmethod
    def add_doc_type(db: Session, doc: DocTypeCreate):
        db_doc_type = DocType(
            label=doc.label,
            description=doc.description,
            example=doc.example,
            prompt=doc.prompt,
            status=doc.status,
            created_by=doc.created_by,
            updated_by=doc.updated_by,
            fid=doc.fid,
        )
        try:
            db.add(db_doc_type)
            db.flush()
            db.commit()
            db.refresh(db_doc_type)
        except Exception as e:
            db.rollback()  # 发生错误时回滚事务
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Insert DocType Error：{str(e)}") from e

    @staticmethod
    def update_doc_type(db: Session, doc: DocTypeUpdate):
        db_doc_type = db.query(DocType).filter(DocType.id == doc.id).first()
        if not db_doc_type:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"DocType[ID:{doc.id}] Not Found")
        db_doc_type.updated_by = doc.updated_by
        db_doc_type.label = doc.label
        db_doc_type.prompt = doc.prompt
        db_doc_type.status = doc.status
        db_doc_type.example = doc.example
        db_doc_type.description = doc.description
        try:
            db.commit()
            db.refresh(db_doc_type)
        except Exception as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Failed to update DocType: {str(e)}") from e
