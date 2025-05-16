import os

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT") or 587),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    VALIDATE_CERTS=True,
)
fast_mail = FastMail(conf)


async def send_temp_password_to_email(email: str, temp_password: str) -> None:
    message = MessageSchema(
        subject="임시 비밀번호 안내",
        recipients=[email],
        body=f"""
        안녕하세요.
        Real 이동영상 시스템입니다.
        
        임시 비밀번호는 아래와 같습니다.
        
        임시 비밀번호: {temp_password}
        
        로그인 후 반드시 비밀번호를 변경해주세요.
        """,
        subtype="plain",
    )
    await fast_mail.send_message(message)
