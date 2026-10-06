# Master Code Wizard Production Configuration

from pydantic_settings import BaseSettings
from pathlib import Path


class DatabaseSettings(BaseSettings):
    url: str = "postgresql://wizard:wizard_password@localhost:5432/wizard_db"
    pool_size: int = 20
    max_overflow: int = 10
    pool_recycle: int = 3600
    pool_pre_ping: bool = True


class RedisSettings(BaseSettings):
    url: str = "redis://localhost:6379/0"
    queue_name: str = "wizard_tasks"
    result_ttl: int = 86400  # 24 hours


class ModelSettings(BaseSettings):
    provider: str = "openai"
    name: str = "gpt-4o-mini"
    api_key: str = ""
    timeout: int = 60
    max_tokens: int = 1200
    temperature: float = 0.1


class Settings(BaseSettings):
    # Application
    app_name: str = "Master Code Wizard"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Paths
    repo_root: Path = Path("./repos")
    work_dir: Path = Path("./work")
    journal_path: Path = Path("./work/journal.jsonl")

    # Storage
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()

    # LLM
    model: ModelSettings = ModelSettings()

    # Task execution
    task_timeout: int = 1800  # 30 minutes
    worker_threads: int = 4
    max_retries: int = 3

    # Semantic search
    embedding_model: str = "text-embedding-3-small"
    vector_dimension: int = 1536
    similarity_threshold: float = 0.7

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        case_sensitive = False


settings = Settings()
