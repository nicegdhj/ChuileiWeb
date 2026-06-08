from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_base_url: str = "http://localhost:9092/v1"
    llm_model: str = "qwen3-32b"
    llm_max_tokens: int = 32000
    llm_api_key: str = ""
    llm_timeout_seconds: int = 300

    db_url: str = "sqlite:///./data/db/chatbox.sqlite"
    upload_dir: str = "./data/uploads"
    xinling_api_base_url: str = "https://188.107.159.161:19980/test/stream-api/view"

    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
