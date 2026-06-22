"""
config.py — Centralised settings loaded from .env
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_model: str = "mistralai/mixtral-8x7b-instruct"
    openrouter_base_url: str = "https://openrouter.ai/api/v1/chat/completions"

    # HuggingFace
    hf_token: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # App
    app_env: str = "development"
    secret_key: str = "change_me"
    allowed_origins: str = "http://localhost:3000"

    # Rate limiting
    rate_limit_per_minute: int = 10

    # Scraper
    scraper_timeout_seconds: int = 120
    use_proxy: bool = False
    proxy_url: str = ""
    scraper_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
