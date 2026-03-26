import threading

import redis
from elasticsearch import Elasticsearch
from fastapi_mail import FastMail, ConnectionConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session

from src.configs import settings  # Assuming your configuration file


class MailClient:
    """Mail 客户端封装（单例模式）"""
    _instance: FastMail = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> FastMail:
        """获取 Mail 单例实例"""
        if cls._instance is None:
            with cls._lock:  # 确保线程安全
                if cls._instance is None:
                    # 创建邮件配置对象
                    mail_config = ConnectionConfig(
                        MAIL_USERNAME=settings.mail.username,
                        MAIL_PASSWORD=settings.mail.password.get_secret_value(),  # 解包 SecretStr
                        MAIL_PORT=settings.mail.port,
                        MAIL_SERVER=settings.mail.server,
                        MAIL_STARTTLS=settings.mail.starttls,
                        MAIL_SSL_TLS=settings.mail.ssl_tls,
                        MAIL_FROM=settings.mail.mail_from,
                        MAIL_FROM_NAME=settings.mail.from_name,
                    )
                    # 创建 FastMail 实例
                    cls._instance = FastMail(mail_config)
        return cls._instance


class ElasticClient:
    """Elasticsearch 客户端封装（单例模式）"""
    _instance: Elasticsearch = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> Elasticsearch:
        """获取 Elasticsearch 单例实例"""
        if cls._instance is None:
            with cls._lock:  # 确保线程安全
                if cls._instance is None:
                    cls._instance = Elasticsearch(
                        hosts=settings.elastic.hosts,
                        basic_auth=(settings.elastic.user, settings.elastic.password.get_secret_value()),
                        ca_certs=settings.elastic.ca_certs,
                        request_timeout=30,
                    )
        return cls._instance


class MysqlClient:
    """MySQL 客户端封装（连接池）"""
    _engine = create_engine(
        settings.db.url,
        pool_size=20,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=3600,
        pool_pre_ping=True,
    )
    _SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=_engine))

    @classmethod
    def get_instance(cls) -> Session:
        """获取数据库会话实例"""
        return cls._SessionLocal()


class RedisClient:
    """Redis 客户端封装（连接池）"""
    _pool = redis.ConnectionPool(
        host=settings.cache.host,
        port=settings.cache.port,
        db=settings.cache.db,
        decode_responses=True,
        max_connections=10  # 允许的最大连接数
    )
    _instance: redis.Redis = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> redis.Redis:
        """获取 Redis 连接池实例"""
        if cls._instance is None:
            with cls._lock:  # 确保线程安全
                if cls._instance is None:
                    cls._instance = redis.Redis(connection_pool=cls._pool)
        return cls._instance
