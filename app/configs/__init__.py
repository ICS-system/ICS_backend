from app.configs.base_settings import Settings


def get_settings() -> Settings:
    return Settings(_env_file="envs/.env.local", _env_file_encoding="utf-8")


settings = get_settings()
