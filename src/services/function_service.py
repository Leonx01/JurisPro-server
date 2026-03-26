from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.error_codes import ErrorCode
from repositories.function_repository import FunctionRepository
from schemas.function_schema import Function, LLMFunctionMatrix, LLMFunctionMatrixUpdate, FunctionVO
from src.exceptions.exception import AppException


class FunctionService:
    @staticmethod
    def get_function_by_id(db: Session, fid: int) -> FunctionVO:
        """ 根据ID获取功能 """
        function = FunctionRepository.get_function_by_id(db, fid)
        return FunctionVO.model_validate(function)

    @staticmethod
    def set_prompt(db: Session, fid: int, pid: int):
        """ 更新功能的提示词 """
        FunctionRepository.set_prompt(db, fid, pid)

    @staticmethod
    def get_function_matrix(db: Session) -> List[LLMFunctionMatrix]:
        """ 获取模型与功能的绑定关系 """
        try:
            function_matrix = FunctionRepository.get_function_matrix(db)
            return function_matrix
        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Database error: {str(e)}") from e

    @staticmethod
    def get_all_functions(db: Session) -> List[FunctionVO]:
        """ 获取所有功能列表 """
        try:
            return FunctionRepository.get_all_functions(db)

        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Database error: {str(e)}") from e

    @staticmethod
    def get_functions(db: Session) -> List[Function]:
        """ 获取功能列表 """
        try:
            db_functions = FunctionRepository.get_base_functions(db)
            functions = [Function.model_validate(f) for f in db_functions]
            return functions
        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Database error: {str(e)}") from e

    @staticmethod
    def update_function_matrix(db: Session, update: LLMFunctionMatrixUpdate):
        """ 更新模型与功能的绑定关系 """
        model_id = update.id
        for function_code in update.functions.keys():
            status = update.functions[function_code]
            if status:
                FunctionRepository.active_func_bind(db, model_id, function_code)
            else:
                FunctionRepository.inactive_func_bind(db, model_id, function_code)
