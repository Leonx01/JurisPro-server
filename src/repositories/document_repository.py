from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.error_codes import ErrorCode
from exceptions.exception import AppException
from models import Document, DocType
from schemas.document_schema import DocumentCreate, DocumentUserPage, DocumentUserMeta, DocumentUpdate
from utils.converters import Converter


class DocumentRepository:
    @staticmethod
    def delete_document(db: Session, doc_id: int):
        """删除文档"""
        db_document = db.query(Document).filter(Document.id == doc_id).first()
        if not db_document:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Document[ID:{doc_id}] Not Found")
        db.delete(db_document)
        try:
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Failed to delete Document: {str(e)}") from e

    @staticmethod
    def get_document_by_id(db: Session, doc_id: int) -> Document:
        """根据ID获取文档"""
        db_document = db.query(Document).filter(Document.id == doc_id).first()
        if not db_document:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Document[ID:{doc_id}] Not Found")
        return db_document

    @staticmethod
    def get_document_by_uuid(db: Session, uuid: str) -> Document:
        """根据UUID获取文档"""
        db_document = db.query(Document).filter(Document.uuid == uuid).first()
        if not db_document:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Document[UUID:{uuid}] Not Found")
        return db_document

    @staticmethod
    def get_documents_by_user(db: Session, user_id: int) -> list[Document]:
        """根据用户ID获取文档列表"""
        db_documents = db.query(Document).filter(Document.created_by == user_id).all()
        if not db_documents:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Documents for User[ID:{user_id}] Not Found")
        return db_documents

    @staticmethod
    def get_user_doc_page(
            db: Session,
            uid: int,
            keyword: str = None,
            tid: int = None,
            page: int = 1,
            page_size: int = 10
    ) -> DocumentUserPage:
        """根据用户ID获取文档列表"""
        try:
            query = db.query(Document).filter(Document.uid == uid)
            if keyword:
                query = query.filter(Document.name.contains(keyword))
            if tid:
                query = query.filter(Document.tid == tid)
            # 处理分页
            query = query.order_by(Document.updated_at.desc())
            total = query.count()  # 总记录数
            documents = query.offset((page - 1) * page_size).limit(page_size).all()

            tid_list = list({doc.tid for doc in documents})
            doc_types = db.query(DocType.id, DocType.label).filter(DocType.id.in_(tid_list)).all()
            tid_to_name = {tid: name for tid, name in doc_types}

            result = []
            for doc in documents:
                meta = DocumentUserMeta.model_validate(doc)
                meta.type = tid_to_name.get(doc.tid, "")
                result.append(meta)
            return DocumentUserPage(
                total=total,
                documents=result
            )
        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Query Document Error: {str(e)}") from e

    @staticmethod
    def add_document(db: Session, document: DocumentCreate):
        db_document = Document(
            uid=document.uid,
            tid=document.tid,
            uuid=document.uuid,
            name=document.name,
            content=Converter().txt_to_html(document.content),
            created_by=document.created_by,
            updated_by=document.updated_by,
        )
        try:
            db.add(db_document)
            db.commit()
            db.refresh(db_document)
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Failed to add Document: {str(e)}") from e

    @staticmethod
    def update_document(db: Session, document: DocumentUpdate):
        db_doc = db.query(Document).filter(Document.uuid == document.uuid).first()
        if document.name:
            db_doc.name = document.name
        if document.content:
            db_doc.content = document.content
        db_doc.updated_by = document.update_by
        try:
            db.commit()
            db.refresh(db_doc)
        except Exception as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Failed to Update Document: {str(e)}") from e
