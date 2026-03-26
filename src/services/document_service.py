import uuid
from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.error_codes import ErrorCode
from exceptions.exception import AppException
from repositories.doc_type_repository import DocTypeRepository
from repositories.document_repository import DocumentRepository
from repositories.function_repository import FunctionRepository
from repositories.prompt_repository import PromptRepository
from repositories.user_repository import UserRepository
from schemas.document_schema import DocTypeCreate, DocTypeUpdate, DocumentCreate, DocumentUserVO, DocumentUserPage, \
    DocumentUpdate
from schemas.document_schema import DocTypeUserVO
from schemas.function_schema import FunctionCreate
from schemas.prompt_schema import PromptTemplate
from services.llm_service import LLMService


class DocumentService:
    @staticmethod
    def get_user_doc(db: Session, uname: str, keyword: str, tid: int, page: int, page_size: int) -> DocumentUserPage:
        """根据用户ID获取文档列表"""
        user = UserRepository.get_by_uname(db, uname)
        if not user:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"User[ID:{uname}] Not Found")
        uid = user.uid
        page = DocumentRepository.get_user_doc_page(db, uid, keyword, tid, page, page_size)
        return page

    @staticmethod
    def get_user_doc_types(db: Session) -> List[DocTypeUserVO]:
        try:
            types = DocTypeRepository.get_available_doc_types(db)
            return [DocTypeUserVO.model_validate(_type) for _type in types]
        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Database error: {str(e)}") from e

    # Document Type Management
    @staticmethod
    def update_doc_type(db: Session, doc: DocTypeUpdate):
        try:
            DocTypeRepository.update_doc_type(db, doc)
        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Database error: {str(e)}") from e

    @staticmethod
    def add_doc_type(db: Session, doc: DocTypeCreate):
        try:
            function = FunctionCreate(
                name=f"{doc.label}生成",
                code=uuid.uuid4().hex,
                pid=2,
                need_prompt="1",
            )
            fid = FunctionRepository.add_function(db, function)
            doc.fid = fid
            DocTypeRepository.add_doc_type(db, doc)
        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Database error: {str(e)}") from e

    @staticmethod
    def get_doc_types(db: Session, keyword: str, status: str):
        try:
            types = DocTypeRepository.get_doc_types(db, keyword, status)
            return types
        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Database error: {str(e)}") from e

    @staticmethod
    def delete_doc_type(db: Session, doc_id: int):
        try:
            DocTypeRepository.delete_doc_type(db, doc_id)
        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Database error: {str(e)}") from e

    @staticmethod
    def add_doc(db: Session, doc: DocumentCreate):
        user = UserRepository.get_by_uname(db, doc.created_by)
        if not user:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"User[ID:{doc.created_by}] Not Found")
        doc.uid = user.uid
        doctype = DocTypeRepository.get_doc_type_by_id(db, doc.tid)
        if not doctype:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"DocType[ID:{doc.tid}] Not Found")
        function = FunctionRepository.get_function_by_id(db, doctype.fid)
        if not function:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Function[ID:{doc.fid}] Not Found")
        prompt = PromptRepository.get_prompt_by_id(db, function.prompt_id)
        if not prompt:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Prompt[ID:{function.prompt_id}] Not Found")
        template = PromptTemplate(
            content=prompt.prompt,
            slots=function.slots
        )
        slots_value = {"query": doc.query}
        doc.name = LLMService.generate_response_by_code(db, 'summary', doc.query)
        msg = LLMService.generate_with_prompt(db, doc.mid, template, slots_value)
        doc.content = msg.content
        DocumentRepository.add_document(db, doc)

    @staticmethod
    def get_document_by_uuid(db: Session, _uuid: str) -> DocumentUserVO:
        """根据UUID获取文档"""
        document = DocumentRepository.get_document_by_uuid(db, _uuid)
        return DocumentUserVO.model_validate(document)

    @staticmethod
    def delete_document(db: Session, doc_id: int):
        """根据ID删除文档"""
        DocumentRepository.delete_document(db, doc_id)

    @staticmethod
    def update_document(db: Session, doc: DocumentUpdate):
        DocumentRepository.update_document(db, doc)
