import re
from typing import List

from langchain_core.messages import BaseMessage
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.error_codes import ErrorCode
from repositories.function_repository import FunctionRepository
from schemas.llm_schema import GenerativeModelUserVO, GenerativeModelAdminVO, GenerativeModelCreate, \
    GenerativeModelUpdate
from schemas.prompt_schema import PromptTemplate
from services.factory import LLMFactory
from services.prompt_service import PromptService
from src.exceptions.exception import AppException
from src.repositories.llm_repository import LLMRepository
from utils.converters import Converter


class LLMService:
    @staticmethod
    def get_suggestions(db: Session, query: str) -> list[str]:
        content = LLMService.generate_response_by_code(db, 'suggest', query)

        if not content:
            return []

        # 去除开头/结尾空白符（空格、换行等）
        content = content.strip()

        # 替换常见的中文分隔符为英文竖线 |
        # 包括中文竖线 ｜、顿号、逗号、句号、分号、换行等
        content = re.sub(r'[｜、，。；;\n]+', '|', content)

        # 统一多个竖线为一个竖线
        content = re.sub(r'\|{2,}', '|', content)
        content = content.replace('?', '')
        # 再次 strip 并按竖线切分
        suggestions = [f'{item.strip()}？' for item in content.split('|') if item.strip()]

        # 可选：最多保留 3 项（避免模型超额输出）
        return suggestions[:3]

    @staticmethod
    def generate_response_by_code(db: Session, code: str = '', query: str = '') -> str:
        """ 调用 LLM 进行推理 """
        function = FunctionRepository.get_function_by_code(db, code)
        prompt = PromptService.get_prompt_by_id(db, function.prompt_id)
        models = LLMRepository.get_llm_by_function(db, function.code)
        if not models:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"LLM not found for function code: {function.code}")
        template = PromptTemplate(
            content=prompt.prompt,
            slots=function.slots
        )
        print(template)
        slots_value = {"query": query}
        msg = LLMService.generate_with_prompt(db, models[0].id, template, slots_value)
        print(msg)
        if msg.response_metadata.__contains__('model') and "deepseek" in msg.response_metadata['model']:
            msg.content = Converter.deepseek_format(msg.content)
        return msg.content

    # @staticmethod
    # def rewrite(db: Session, fid: int = 9) -> BaseMessage:
    #     """ 调用 LLM 进行推理 """
    #     # 获取 LLM 实例
    #     llm = LLMFactory.get_llm(db, model_id)
    #     # 调用 LLM 进行推理
    #     response = llm.invoke(prompt)
    #     return response

    @staticmethod
    def generate_with_prompt(db: Session, model_id: int, template: PromptTemplate, slots_value: dict) -> BaseMessage:
        # Prompt <---- DocType <------- Function
        prompt = template.content
        for key, value in slots_value.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
        print(prompt)
        llm = LLMFactory.get_llm(db, model_id)
        response = llm.invoke(prompt)
        # Prompt <---- Function
        return response

    @staticmethod
    def llm_invoke(user_input: dict, prompt_id: int, model_id: int, db: Session) -> None:
        pass
        """
        1. 查询数据库获取 Prompt 模板
        2. 使用用户输入填充 Prompt
        3. 调用 LLM 进行推理
        """
        # 1. 查询 Prompt
        # prompt_entry = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        # if not prompt_entry:
        #     raise AppException(ErrorCode.PROMPT_NOT_FOUND, f"Prompt ID={prompt_id} not found.")
        #
        # prompt_template = prompt_entry.prompt_template
        #
        # # 2. 使用用户输入填充 Prompt
        # try:
        #     prompt = prompt_template.format(**user_input)
        # except KeyError as e:
        #     raise AppException(ErrorCode.INVALID_INPUT, f"Missing input variable: {str(e)}")

        # 3. 获取 LLM 实例
        # try:
        #     llm = LLMFactory.get_llm(model_id, db)
        # except Exception as e:
        #     raise AppException(ErrorCode.MODEL_NOT_FOUND, f"Model not found: {str(e)}") from e
        #
        # # 4. 发送请求到 LLM
        # response = llm.invoke(prompt)
        #
        # # 5. 处理 LLM 返回内容（去除无用标签等）
        # response.content = re.sub(r'<think>\s*</think>\n\n', '', response.content)
        #
        # return response.content

    @staticmethod
    def query_llm(db: Session, keyword: str, _type: str, status: str) -> List[GenerativeModelAdminVO]:
        """ 获取 LLM 列表 """
        try:
            models = LLMRepository.get_llm_list(db, keyword, _type, status)
            return models
        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Database error: {str(e)}") from e

    @staticmethod
    def get_by_function(db: Session, function_name: str) -> List[GenerativeModelUserVO]:
        """ 根据功能名称获取已启用绑定的模型列表 """
        try:
            llm_list = LLMRepository.get_llm_by_function(db, function_name)
            return [GenerativeModelUserVO.model_validate(llm) for llm in llm_list]

        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Database error: {str(e)}") from e

    @staticmethod
    def ping(db: Session, model_id: int):
        """ 测试 LLM 是否可用 """
        try:
            llm = LLMFactory.get_llm(db, model_id)
            msg = llm.invoke("你好!")
            # print(BaseMessage.pretty_repr(msg))
            print(msg)
            LLMRepository.update_connection(db, model_id, "1")
            return msg.content
        except Exception as e:
            LLMRepository.update_connection(db, model_id, "2")
            raise AppException(ErrorCode.MODEL_NOT_AVAILABLE, f"Model not available: {str(e)}") from e

    @staticmethod
    def add_llm(db: Session, model: GenerativeModelCreate):
        """ 添加 LLM """
        LLMRepository.add_llm(db, model)

    @staticmethod
    def delete_llm(db: Session, model_id: int):
        """ 删除 LLM """
        LLMRepository.delete_llm(db, model_id)

    @staticmethod
    def update_llm(db: Session, model: GenerativeModelUpdate):
        """ 更新 LLM """
        LLMRepository.update_llm(db, model)
