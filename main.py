import os
print("🔥 ENV_FILE:", os.environ.get("ENV_FILE"))

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware
from app.configs.database_settings import TORTOISE_ORM


load_dotenv(dotenv_path="envs/.env.local")

DB_URL = os.getenv("DB_URL")

app = FastAPI()

# 로그인 이후 프로필 정보 변경 시 나타나는 422 오류 로그 확인
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    print(f"422 오류 발생: {exc_str}")
    content = {
        "status_code": 10422,
        "message": exc_str,
        "data": None,
    }
    return JSONResponse(
        content,
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY)

# CORS 미들웨어 관리
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://192.168.0.151:5173",
        "https://localhost:5173",
        "http://192.168.0.151:5173",
        "http://localhost:5173",
        "http://3.34.75.129",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# tortoise orm 관리
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)

# 라우터 등록 관리
from app.routers.user_router import router as user_router
from app.routers.live_router import router as live_router

app.include_router(user_router, prefix="/api")
app.include_router(live_router, prefix="/api")