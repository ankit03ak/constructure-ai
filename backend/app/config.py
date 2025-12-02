from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    app_host: str = "0.0.0.0"
    app_port: int = 8080

    cors_origins: List[str] = []

    session_secret_key: str
    access_token_expire_minutes: int = 60 * 24

    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    google_oauth_scopes: str

    gemini_api_key: str

    frontend_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
