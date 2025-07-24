import os
from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(StrEnum):
    LOCAL = "local"
    STAGE = "stage"
    PROD = "prod"

class Settings(BaseSettings):
    ENV: Env = Env.LOCAL
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_DB: str

    SECRET_KEY: str

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str

    class Config:
        extra = "allow"

env_file_path = os.environ.get("ENV_FILE", "envs/.env.local")
print(f"✅ env_file_path: {env_file_path}")
settings = Settings(_env_file=env_file_path)