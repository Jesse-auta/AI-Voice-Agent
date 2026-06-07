from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # VAPI
    vapi_api_key: str
    vapi_webhook_secret: str = ""

    # Database
    database_url: str

    # App
    base_url: str = "http://localhost:8000"
    environment: str = "development"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()