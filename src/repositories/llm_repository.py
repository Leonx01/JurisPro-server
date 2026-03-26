from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.error_codes import ErrorCode
from exceptions.exception import AppException
from models import GenerativeModel, LLMFunction, LLMFunctionBinding
from schemas.llm_schema import GenerativeModelAdminVO, GenerativeModelCreate, GenerativeModelUpdate


class LLMRepository:
    @staticmethod
    def update_llm(db: Session, model: GenerativeModelUpdate):
        db_model = db.query(GenerativeModel).filter(GenerativeModel.id == model.id).first()
        if not db_model:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Model[ID:{model.id}] Not Found")
        db_model.label = model.label
        db_model.name = model.name
        db_model.type = model.type
        db_model.provider = model.provider
        db_model.api_key = model.api_key
        db_model.description = model.description
        db_model.status = model.status
        db_model.updated_by = model.updated_by
        try:
            db.commit()
            db.refresh(db_model)
        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Update LLM Error: {str(e)}") from e

    @staticmethod
    def delete_llm(db: Session, model_id: int):
        model = db.query(GenerativeModel).filter(GenerativeModel.id == model_id).first()
        if not model:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Model[ID:{model_id}] Not Found")
        model.is_deleted = "1"
        try:
            db.commit()
            db.refresh(model)
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Failed to delete model: {str(e)}") from e

    @staticmethod
    def add_llm(db: Session, model: GenerativeModelCreate):
        """添加 LLM 模型"""
        db_model = GenerativeModel(
            label=model.label,
            name=model.name,
            type=model.type,
            provider=model.provider,
            api_key=model.api_key,
            description=model.description,
            status=model.status,
            created_by=model.created_by,
            updated_by=model.updated_by,
        )
        try:
            db.add(db_model)
            db.flush()
            db.commit()
            db.refresh(db_model)
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Insert LLM Error: {str(e)}") from e

    @staticmethod
    def update_connection(db: Session, model_id: int, connection: str):
        """设置数据库连接"""
        # 查询模型对象
        model = db.query(GenerativeModel).filter(GenerativeModel.id == model_id,
                                                 GenerativeModel.is_deleted == "0").first()
        if not model:
            raise AppException(ErrorCode.MODEL_NOT_AVAILABLE, f"Model ID={model_id} not found.")
        try:
            model.connection = connection
            db.commit()
            db.refresh(model)
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Failed to update model status: {str(e)}") from e

    @staticmethod
    def get_llm_by_function(db: Session, function_code: str) -> List[GenerativeModel]:
        """根据功能名称获取已启用绑定的模型列表"""
        # 查询功能对象
        function = db.query(LLMFunction).filter(LLMFunction.code == function_code).first()
        if not function:
            return []

        # 获取所有绑定的模型 ID（状态为启用）
        binding_model_ids = db.query(LLMFunctionBinding.llm_id).filter(
            LLMFunctionBinding.function_id == function.id,
        ).distinct().all()  # 使用 .all() 获取所有结果，返回一个列表

        # 如果没有绑定的模型，返回空列表
        if not binding_model_ids:
            return []

        # 提取所有模型 ID
        binding_model_ids = [model_id[0] for model_id in binding_model_ids]  # 仅提取 llm_id 部分

        # 查询对应模型
        models = db.query(GenerativeModel).filter(
            GenerativeModel.is_deleted == "0",
            GenerativeModel.status == "1",
            GenerativeModel.id.in_(binding_model_ids)
        ).all()

        return models

    @staticmethod
    def get_llm_list(db: Session, keyword: str = None, _type: str = None, status: str = None) -> List[
        GenerativeModelAdminVO]:
        """获取模型列表"""
        query = db.query(GenerativeModel).filter(GenerativeModel.is_deleted == "0")

        if keyword:
            query = query.filter(GenerativeModel.name.like(f"%{keyword}%"))
        if _type:
            query = query.filter(GenerativeModel.type == _type)
        if status:
            query = query.filter(GenerativeModel.status == status)

        models = query.all()
        return [GenerativeModelAdminVO.model_validate(model) for model in models]
