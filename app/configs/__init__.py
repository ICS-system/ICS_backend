from app.configs.base_settings import Settings
from pathlib import Path
import os

def get_settings() -> Settings:
    env_path = os.environ.get("ENV_FILE", "envs/.env.local")
    return Settings(_env_file=Path(env_path), _env_file_encoding="utf-8")

settings = get_settings()
