from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

EMBEDDING_DIMENSIONS = 768


class Settings(BaseSettings):
    database_url: str

    app_name: str = "AI WorkHub API"
    app_version: str = "0.1.0"
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:3000"]

    storage_dir: str = "storage"
    max_upload_mb: int = 10
    max_pages: int = 300

    gemini_api_key: str = ""
    llm_model: str = "gemini-3.8-flash"
    embedding_model: str = "gemini-embedding-2"

    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_top_k: int = 5
    min_similarity: float = 0.30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def embedding_signature(self) -> str:
        return f"{self.embedding_model}:{EMBEDDING_DIMENSIONS}"


@lru_cache
def get_settings() -> Settings:
    return Settings()