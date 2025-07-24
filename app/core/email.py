import os

from app.configs.base_settings import settings
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema


def get_fast_mail() -> FastMail:
    conf = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        VALIDATE_CERTS=True,
    )
    return FastMail(conf)

async def send_temp_password_to_email(email: str, temp_password: str) -> None:
    message = MessageSchema(
        subject="임시 비밀번호 안내",
        recipients=[email],
        body=f"임시 비밀번호: {temp_password}",
        subtype="plain",
    )
    await get_fast_mail().send_message(message)
