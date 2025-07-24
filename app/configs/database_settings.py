from app.configs import settings

TORTOISE_APP_MODELS = [
    "aerich.models",
    "app.models.user_model",
]

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": settings.DB_HOST,
                "port": settings.DB_PORT,
                "user": settings.DB_USER,
                "password": settings.DB_PASSWORD,
                "database": settings.DB_DB,
                "connect_timeout": 5,
                "minsize": 15,
                "maxsize": 500,
                "pool_recycle": 3600,
            },
        },
    },
    "apps": {
        "modules": {
            "models": TORTOISE_APP_MODELS,
        },
    },
    # "routers": ["app.configs.database_config.Router"],
    "timezone": "Asia/Seoul",
}
