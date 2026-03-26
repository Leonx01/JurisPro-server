from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="DATABASE_", extra="ignore")
    user: str
    password: SecretStr
    host: str
    port: int
    name: str

    @property
    def url(self) -> str:
        return f"mysql+mysqldb://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"

class SentenceTransformerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="SENTENCE_TRANSFORMER_", extra="ignore")
    model: str

class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="REDIS_", extra="ignore")
    host: str
    port: int
    db: int

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"


class MailSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="MAIL_", extra="ignore")
    username: str
    password: SecretStr
    mail_from: str
    port: int
    server: str
    ssl_tls: bool
    starttls: bool
    template_path: str
    from_name: str


class ElasticSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ELASTIC_", extra="ignore")
    hosts: str
    user: str
    password: SecretStr
    ca_certs: str


class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="JWT_", extra="ignore")
    secret_key: SecretStr
    expires_in: int = 86400  # 默认 24 小时


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")
    title: str
    debug: bool
    port: int
    host: str
    db: DatabaseSettings = DatabaseSettings()
    cache: RedisSettings = RedisSettings()
    mail: MailSettings = MailSettings()
    elastic: ElasticSettings = ElasticSettings()
    sentence_transformer: SentenceTransformerSettings = SentenceTransformerSettings()
    jwt: JWTSettings = JWTSettings()


settings = AppSettings()
