import os
from enum import StrEnum

from pydantic_settings import BaseSettings


class Env(StrEnum):
    LOCAL = "local"
    STAGE = "stage"
    PROD = "prod"

env = os.getenv("ENV", "local").lower()

# 환경에 맞는 .env 경로 매핑
env_path_map = {
    "local": "envs/.env.local",
    "stage": "envs/.env.stage",
    "prod": "envs/.env.prod",
}

env_file_path = env_path_map.get(env, "envs/.env.local")

class Settings(BaseSettings):
    ENV: Env = Env.LOCAL
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_DB: str
    DB_URL: str

    # JWT 설정
    SECRET_KEY: str

    # 메일 설정
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str

    class Config:
        env_file = env_file_path
        extra = "allow"


settings = Settings()
