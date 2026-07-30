from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    FRONTEND_ORIGINS: List[str] = ["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:3000"]
    DEFAULT_PERIOD: str = "6mo"
    DEFAULT_INTERVAL: str = "1d"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()