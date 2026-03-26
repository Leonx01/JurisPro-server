import logging
import threading

from langchain_community.chat_models import ChatTongyi
from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama
from pydantic import SecretStr
from sqlalchemy.orm import Session

from schemas.llm_schema import GenerativeModelConfig
from src.models import GenerativeModel


class LLMFactory:
    """管理本地和云端模型的全局缓存，支持多种模型提供商，线程安全"""

    _lock = threading.Lock()  # 线程锁，保证多线程安全

    @classmethod
    def load_config_from_db(cls, db: Session, model_id: int) -> BaseChatModel | None:
        """使用 SQLAlchemy ORM 方式查询数据库并加载模型配置"""
        try:
            db_model = db.query(GenerativeModel).filter(
                GenerativeModel.is_deleted == "0",
                GenerativeModel.id == model_id).first()
            if not db_model:
                logging.warning(f"❌ 没有找到模型 ID={model_id}")
            try:
                config = GenerativeModelConfig(
                    id=db_model.id,
                    provider=db_model.provider,
                    name=db_model.name,
                    api_key=SecretStr(db_model.api_key) if db_model.api_key else None,
                    # base_url=db_model.base_url,
                )
                return cls.load_model(config)
            except Exception as e:
                logging.error(f"❌ 解析数据库模型配置失败: {e}, 数据: {db_model}")

        except Exception as e:
            logging.error(f"❌ 读取数据库模型配置失败: {e}")

    @staticmethod
    def load_model(config: GenerativeModelConfig) -> BaseChatModel:
        """根据提供商加载不同的模型"""
        try:
            if config.provider == "ollama":
                return ChatOllama(model=config.name)
            elif config.provider == "tongyi":
                return ChatTongyi(
                    model=config.name,
                    api_key=config.api_key.get_secret_value() if config.api_key else None
                )
            else:
                raise ValueError(f"❌ 不支持的模型提供商: {config.provider}")
        except Exception as e:
            logging.error(f"❌ 加载模型失败: {e}, 配置: {config}")
            raise

    @classmethod
    def get_llm(cls, db: Session, model_id: int) -> BaseChatModel:
        """获取 LLM 实例，线程安全"""
        with cls._lock:
            return cls.load_config_from_db(db, model_id)
