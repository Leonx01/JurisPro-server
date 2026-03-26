from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.error_codes import ErrorCode
from exceptions.exception import AppException
from models import Prompt
from repositories.function_repository import FunctionRepository
from schemas.prompt_schema import PromptCreate, PromptVO, PromptUpdate, PromptPage


class PromptRepository:
    @staticmethod
    def query_prompt_page(
            db: Session,
            keyword: str = None,
            fid: int = None,
            page: int = 1,
            page_size: int = 10
    ) -> PromptPage:
        try:
            query = db.query(Prompt)

            if fid:
                fid = FunctionRepository.get_base_id(db, fid)
                query = query.filter(Prompt.fid == fid)

            if keyword:
                query = query.filter(Prompt.name.contains(keyword))

            total = query.count()  # 总记录数
            prompts = query.offset((page - 1) * page_size).limit(page_size).all()

            return PromptPage(
                total=total,
                prompts=[PromptVO.model_validate(prompt) for prompt in prompts],
            )
        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Query Prompt Error: {str(e)}") from e

    @staticmethod
    def get_prompt_by_id(db: Session, pid: int) -> Prompt:
        """根据ID获取提示词"""
        db_prompt = db.query(Prompt).filter(Prompt.id == pid).first()
        if not db_prompt:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Prompt[ID:{pid}] Not Found")
        return db_prompt

    @staticmethod
    def delete_prompt(db: Session, pid: int):
        db_prompt = db.query(Prompt).filter(Prompt.id == pid).first()
        if not db_prompt:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Prompt [ID:{pid}] Not Found")
        try:
            db.delete(db_prompt)
            db.commit()
        except Exception as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Failed to delete Prompt: {str(e)}") from e

    @staticmethod
    def update_prompt(db: Session, prompt: PromptUpdate):
        try:
            db_prompt = db.query(Prompt).filter(Prompt.id == prompt.id).first()
            if not db_prompt:
                raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Prompt[ID:{prompt.id}] Not Found ")
            db_prompt.prompt = prompt.prompt
            db_prompt.updated_by = prompt.updated_by
            db_prompt.name = prompt.name
            db_prompt.fid = prompt.fid
            db_prompt.description = prompt.description
            db.commit()
            db.refresh(db_prompt)
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED)
        except AppException as e:
            raise e

    @staticmethod
    def query_prompt(db: Session, keyword: str = None, fid: int = None) -> List[PromptVO]:
        try:
            query = db.query(Prompt)
            if fid:
                fid = FunctionRepository.get_base_id(db, fid)
                query = query.filter(Prompt.fid == fid)
            if keyword:
                query = query.filter(Prompt.name.contains(keyword))
            prompts = query.all()
            return [PromptVO.model_validate(prompt) for prompt in prompts]
        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Insert Prompt Error: {str(e)}") from e

    @staticmethod
    def get_all_prompt(db: Session) -> List[PromptVO]:
        try:
            prompts = db.query(Prompt).all()
            return [PromptVO.model_validate(prompt) for prompt in prompts]
        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Insert Prompt Error: {str(e)}") from e

    @staticmethod
    def add_prompt(db: Session, prompt: PromptCreate):

        """添加提示词"""
        db_prompt = Prompt(
            name=prompt.name,
            description=prompt.description,
            fid=prompt.fid,
            prompt=prompt.prompt,
            created_by=prompt.created_by,
            updated_by=prompt.updated_by
        )
        try:
            db.add(db_prompt)
            db.flush()
            db.commit()
            db.refresh(db_prompt)

        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Insert Prompt Error: {str(e)}") from e
