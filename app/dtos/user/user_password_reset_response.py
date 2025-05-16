from pydantic import BaseModel


# 비밀번호 찾기
class UserPasswordResetResponse(BaseModel):
    message: str


# 비밀번호 변경
class UserPasswordChangeResponse(BaseModel):
    message: str
