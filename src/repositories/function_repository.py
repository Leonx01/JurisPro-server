from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.error_codes import ErrorCode
from exceptions.exception import AppException
from models import GenerativeModel, LLMFunction, LLMFunctionBinding
from schemas.function_schema import LLMFunctionMatrix, FunctionCreate, FunctionVO


class FunctionRepository:

    @staticmethod
    def get_function_by_code(db: Session, function_code: str) -> LLMFunction:
        """根据功能代码获取功能"""
        db_function = db.query(LLMFunction).filter(LLMFunction.code == function_code).first()
        if not db_function:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Function[Code:{function_code}] Not Found")
        return db_function

    @staticmethod
    def get_function_by_id(db: Session, function_id: int) -> LLMFunction:
        """根据ID获取功能"""
        db_function = db.query(LLMFunction).filter(LLMFunction.id == function_id).first()
        if not db_function:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Function[ID:{function_id}] Not Found")
        return db_function

    @staticmethod
    def set_prompt(db: Session, function_id: int, prompt_id: int) -> None:
        """设置功能的提示词"""
        # 查询功能对象
        function = db.query(LLMFunction).filter(LLMFunction.id == function_id).first()
        if not function:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Function[ID:{function_id}] Not Found")

        # 设置提示词
        function.prompt_id = prompt_id
        try:
            db.commit()
            db.refresh(function)
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Set Function Prompt Error: {str(e)}") from e

    @staticmethod
    def get_base_id(db: Session, sub_id: int) -> int:

        """获取功能ID，通过子ID级联查询父ID，直到找到父ID为null的节点"""
        function = db.query(LLMFunction).filter(LLMFunction.id == sub_id).first()

        if not function:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Function[ID:{sub_id}] Not Found")
        while function.pid:
            function = db.query(LLMFunction).filter(LLMFunction.id == function.pid).first()
            if not function:
                raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Parent Function[ID:{function.pid}] Not Found")

        return function.id

    @staticmethod
    def bind_prompt(db: Session, prompt_id: int, fid: int):
        """绑定功能"""
        # 查询功能对象
        function = db.query(LLMFunction).filter(LLMFunction.id == fid).first()
        if not function:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Function[ID:{fid}] Not Found")

        function.prompt_id = prompt_id
        try:
            db.commit()
            db.refresh(function)
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Insert Function Error: {str(e)}") from e

    @staticmethod
    def get_all_functions(db: Session) -> List[FunctionVO]:
        """获取所有功能列表，并构造层级关系"""
        # Fetch all functions with status '1'
        functions = db.query(LLMFunction).filter(LLMFunction.status == '1').all()

        # Convert to FunctionVO objects
        functions_vo = [FunctionVO.model_validate(function) for function in functions]

        # Create a map of function ID to FunctionVO for easy lookup
        function_map = {function.id: function for function in functions_vo}

        # Initialize a list to hold the root functions
        root_functions = []

        # Build the hierarchy by assigning children
        for function in functions_vo:
            # If the function has a parent (pid), find the parent and add it to the parent's children
            if function.pid:
                parent_function = function_map.get(function.pid)
                if parent_function:
                    if not hasattr(parent_function, 'children'):
                        parent_function.children = []
                    parent_function.children.append(function)
            else:
                # If there's no parent, it's a root function
                root_functions.append(function)

        return root_functions

    @staticmethod
    def get_base_functions(db: Session) -> List[LLMFunction]:
        """获取所有基本功能列表"""
        functions = db.query(LLMFunction).filter(LLMFunction.status == '1', LLMFunction.pid.is_(None)).all()
        return functions

    @staticmethod
    def inactive_func_bind(db: Session, llm_id: int, function_code: str):
        """解除功能绑定"""
        # 查询功能对象
        function = db.query(LLMFunction).filter(LLMFunction.code == function_code).first()
        if not function:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Function[Code:{function_code}] Not Found")

        # 查询绑定关系
        binding = db.query(LLMFunctionBinding).filter(
            LLMFunctionBinding.llm_id == llm_id,
            LLMFunctionBinding.function_id == function.id
        ).first()

        if not binding:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Function[Code:{function_code}] Not Bound")
        else:
            try:
                db.delete(binding)
                db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Failed to unbind function: {str(e)}")

    @staticmethod
    def active_func_bind(db: Session, llm_id: int, function_code: str):
        """激活功能绑定"""
        # 查询功能对象
        function = db.query(LLMFunction).filter(LLMFunction.code == function_code).first()
        if not function:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Function[Code:{function_code}] Not Found")

        # 查询是否已经存在绑定关系
        binding = db.query(LLMFunctionBinding).filter(
            LLMFunctionBinding.llm_id == llm_id,
            LLMFunctionBinding.function_id == function.id
        ).first()

        if binding:
            raise AppException(ErrorCode.RESOURCE_ALREADY_EXISTS, f"Function[Code:{function_code}] Already Bound")
        else:
            try:
                new_binding = LLMFunctionBinding(
                    llm_id=llm_id,
                    function_id=function.id,
                )
                db.add(new_binding)
                db.commit()
                db.refresh(new_binding)
            except SQLAlchemyError as e:
                db.rollback()
                raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Failed to bind function: {str(e)}")

    @staticmethod
    def get_function_matrix(db: Session) -> List[LLMFunctionMatrix]:
        models = db.query(GenerativeModel).filter(GenerativeModel.is_deleted == '0').all()
        all_functions = db.query(LLMFunction).filter(LLMFunction.status == '1').all()

        # function_id -> function_name
        function_mapping = {f.id: f.code for f in all_functions}
        function_codes = list(function_mapping.values())

        # 获取所有启用的绑定关系
        bindings = db.query(LLMFunctionBinding).all()

        from collections import defaultdict
        model_func_map = defaultdict(set)
        for b in bindings:
            function_code = function_mapping.get(b.function_id)
            if function_code:
                model_func_map[b.llm_id].add(function_code)

        result = []
        for model in models:
            func_dict = {
                code: code in model_func_map[model.id]
                for code in function_codes
            }

            result.append(LLMFunctionMatrix(
                label=model.label,
                id=model.id,
                functions=func_dict
            ))

        return result

    @staticmethod
    def add_function(db: Session, function: FunctionCreate) -> int:
        """添加功能"""
        parent_function = db.query(LLMFunction).filter(LLMFunction.id == function.pid).first()
        if not parent_function:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Parent Function[ID:{function.pid}] Not Found")
        db_function = LLMFunction(
            code=function.code,
            name=function.name,
            pid=function.pid,
            slots=parent_function.slots,
        )
        try:
            db.add(db_function)
            db.commit()
            db.refresh(db_function)
            return db_function.id
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Insert Function Error: {str(e)}") from e
