import random
import string

from fastapi import HTTPException, status
from passlib.context import CryptContext
from typing_extensions import Optional

from app.core.email import send_temp_password_to_email
from app.dtos.user.user_login_request import UserLoginRequest
from app.dtos.user.user_login_response import UserLoginResponse
from app.dtos.user.user_password_reset_request import (
    UserPasswordChangeRequest,
    UserPasswordResetRequest,
)
from app.dtos.user.user_password_reset_response import (
    UserPasswordChangeResponse,
    UserPasswordResetResponse,
)
from app.dtos.user.user_profile_update_request import UserProfileUpdateRequest
from app.dtos.user.user_profile_update_response import UserProfileUpdateResponse
from app.dtos.user.user_signup_request import UserSignupRequest
from app.dtos.user.user_signup_response import UserGetResponse, UserSignupResponse
from app.models.user_model import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 회원가입
async def service_signup_user(data: UserSignupRequest) -> UserSignupResponse:
    """
    username, email 중복확인 반영
    """
    # username 중복 체크
    if await User.filter(username=data.username).exists():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 사용 중인 아이디입니다.")

    # email 중복 체크
    if await User.filter(email=data.email).exists():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 사용 중인 이메일입니다.")

    hashed_password = pwd_context.hash(data.password)
    user = await User.create(
        username=data.username,
        password=hashed_password,
        full_name=data.full_name,
        email=data.email,
    )
    return UserSignupResponse(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
    )


# 사용자 정보 조회
async def service_get_user(user_id: int) -> UserGetResponse:
    user = await User.get(id=user_id)
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "사용자를 찾을 수 없습니다.")
    return UserGetResponse(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
    )


# 로그인
async def service_login_user(data: UserLoginRequest) -> UserLoginResponse:
    user = await User.filter(username=data.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="존재하지 않는 아이디입니다.")
    if not pwd_context.verify(data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="비밀번호가 일치하지 않습니다.")
    return UserLoginResponse(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
    )


# 로그인 후 실제 유저
async def authenticate_user(username: str, password: str) -> Optional[User]:
    user = await User.filter(username=username).first()
    if not user:
        return None
    if not pwd_context.verify(password, user.password):
        return None
    return user


# 임시 비밀번호 생성
def generate_temp_password(length: int = 10) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


# 비밀번호 리셋
async def service_reset_password(data: UserPasswordResetRequest) -> UserPasswordResetResponse:
    user = await User.filter(email=data.email, full_name=data.full_name).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="일치하는 사용자가 없습니다.")
    await user.save()

    temp_password = generate_temp_password()
    hashed_password = pwd_context.hash(temp_password)
    user.password = hashed_password
    await user.save()

    # 이메일 발송
    await send_temp_password_to_email(user.email, temp_password)

    return UserPasswordResetResponse(message=f"임시 비밀번호가 {user.email}로 발송되었습니다.")


# 비밀번호 변경
async def service_change_password(user_id: int, data: UserPasswordChangeRequest) -> UserPasswordChangeResponse:
    user = await User.get(id=user_id)
    if not pwd_context.verify(data.old_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="기존 비밀번호가 일치하지 않습니다.")
    user.password = pwd_context.hash(data.new_password)
    await user.save()
    return UserPasswordChangeResponse(message="비밀번호가 성공적으로 변경되었습니다.")


# 프로필 정보 변경
async def service_update_profile(user_id: int, data: UserProfileUpdateRequest) -> dict[str, str]:
    user = await User.get(id=user_id)
    if data.full_name:
        user.full_name = data.full_name
    if data.email:
        user.email = data.email
    await user.save()
    return {"message": "프로필 정보가 성공적으로 변경되었습니다."}
