from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CreditWise AI"
    secret_key: str = "dev-secret-change-me"
    database_url: str = "sqlite:///./creditwise.db"
    environment: str = "development"
    model_path: str = "app/ml/artifacts/model.joblib"
    model_metrics_path: str = "app/ml/artifacts/metrics.json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
