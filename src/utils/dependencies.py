import asyncio

from elasticsearch import Elasticsearch
from fastapi import Depends
from fastapi_mail import FastMail
from redis import Redis
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from configs import settings
from main import oauth2_scheme
from src.utils.clients import MysqlClient, RedisClient, ElasticClient, MailClient


# async def get_db():
#     """FastAPI 依赖注入 - MySQL 数据库会话"""
#     db: Session = MysqlClient.get_instance()
#     try:
#         yield db
#     finally:
#         db.close()


async def get_db():
    """FastAPI 依赖注入 - MySQL 数据库会话（异步处理同步操作）"""
    # 使用 asyncio.to_thread 来执行同步操作
    db: Session = await asyncio.to_thread(MysqlClient.get_instance)

    try:
        yield db
    finally:
        # 使用 asyncio.to_thread 关闭数据库会话
        await asyncio.to_thread(db.close)


async def get_redis():
    """FastAPI 依赖注入 - Redis 连接"""
    redis_client: Redis = RedisClient.get_instance()
    yield redis_client


async def get_elastic():
    """FastAPI 依赖注入 - Elasticsearch 连接"""
    es_client: Elasticsearch = ElasticClient.get_instance()
    yield es_client  # ES 客户端一般不需要关闭，避免频繁重建连接


async def get_smtp():
    """获取 MailClient 实例（用于 FastAPI 依赖注入）"""
    mail_client: FastMail = MailClient.get_instance()
    yield mail_client


async def embed():
    model: SentenceTransformer = SentenceTransformer(settings.sentence_transformer.model)
    yield model


from src.utils.generators import JwtToken


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """FastAPI 依赖注入 - 获取当前用户"""
    try:
        payload = JwtToken.validate_and_parse(token)
        return payload  # 可以返回解析后的用户信息
    except Exception as e:
        raise e
