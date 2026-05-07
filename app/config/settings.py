from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "TCM RAG Service"
    app_env: str = "local"
    debug: bool = False

    mysql_dsn: str = "mysql+pymysql://user:password@127.0.0.1:3306/tcm_rag?charset=utf8mb4"
    redis_url: str = "redis://127.0.0.1:6379/0"
    milvus_uri: str = "http://127.0.0.1:19530"
    milvus_token: str | None = None
    milvus_timeout_seconds: float = 10

    llm_api_endpoint: str | None = None
    llm_api_key: str | None = None
    llm_model_name: str | None = None
    llm_max_tokens: int = 1024
    llm_temperature: float = 0.3

    embedding_api_endpoint: str | None = None
    embedding_api_key: str | None = None
    embedding_model_name: str | None = None
    embedding_dimension: int = Field(default=1024, ge=1)

    symptom_high_confidence: float = Field(default=0.82, ge=0, le=1)
    symptom_low_confidence: float = Field(default=0.65, ge=0, le=1)
    max_followup_rounds: int = Field(default=2, ge=0)
    session_ttl_seconds: int = Field(default=1800, ge=60)
    context_max_tokens: int = Field(default=4096, ge=512)

    product_text_weight: float = 0.4
    product_tcm_weight: float = 0.4
    product_business_weight: float = 0.2

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production", "false", "0", "no"}:
                return False
            if normalized in {"dev", "local", "debug", "true", "1", "yes"}:
                return True
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
