from pydantic import BaseModel, EmailStr


# 비밀번호 찾기
class UserPasswordResetRequest(BaseModel):
    email: EmailStr
    full_name: str


# 비밀번호 변경
class UserPasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str
