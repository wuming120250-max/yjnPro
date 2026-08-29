from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    database_url: str = "postgresql+psycopg://postgres@127.0.0.1:5432/yanjiangnan_ai"
    qwen_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("OPENAI_API_KEY", "QWEN_API_KEY"),
    )
    qwen_api_base: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        validation_alias=AliasChoices("OPENAI_BASE_URL", "QWEN_API_BASE"),
    )
    qwen_model: str = Field(
        default="qwen-plus",
        validation_alias=AliasChoices("LLM_MODEL", "QWEN_MODEL"),
    )
    llm_default_temperature: float = Field(default=0.1)
    demo_mode: bool = False
    jwt_secret: str = ""
    admin_username: str = "admin"
    admin_password: str = ""
    store_name: str = "青岛城阳宴江南（汇海路店）"


@lru_cache
def get_settings() -> Settings:
    return Settings()
