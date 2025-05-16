import os

from dotenv import load_dotenv
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

load_dotenv(dotenv_path="envs/.env.local")

DB_URL = os.getenv("DB_URL")

app = FastAPI()

register_tortoise(
    app,
    db_url=DB_URL,
    modules={"models": ["app.models.user_model"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

# 라우터 등록
from app.routers.user_router import router as user_router

app.include_router(user_router)
