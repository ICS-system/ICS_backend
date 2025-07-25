import os
from enum import StrEnum

from pydantic_settings import BaseSettings


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
        env_file = os.environ.get("ENV_FILE") or "/home/ubuntu/ever_real/backend/envs/.env.local"
        env_file_encoding = 'utf-8'

settings = Settings()
