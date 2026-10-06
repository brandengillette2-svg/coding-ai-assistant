from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass
class Settings:
    repo_root: Path = Path(os.getenv("REPO_ROOT", ".")).resolve()
    work_dir: Path = Path(os.getenv("WORK_DIR", "./work")).resolve()
    journal_path: Path = Path(os.getenv("JOURNAL_PATH", "./work/journal.jsonl")).resolve()
    db_path: Path = Path(os.getenv("DB_PATH", "./work/context.db")).resolve()
    model_api_key: str = os.getenv("MODEL_API_KEY", "")
    model_provider: str = os.getenv("MODEL_PROVIDER", "openai")
    model_name: str = os.getenv("MODEL_NAME", "gpt-4o-mini")


settings = Settings()
