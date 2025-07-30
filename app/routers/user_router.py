from string import ascii_lowercase

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt

from app.core.auth import create_access_token, get_current_user, oauth2_scheme, ALGORITHM, SECRET_KEY
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
from app.dtos.user.user_signup_request import UserSignupRequest
from app.dtos.user.user_signup_response import UserGetResponse, UserSignupResponse
from app.models.user_model import User
from app.services.user_service import (
    authenticate_user,
    service_change_password,
    service_get_user,
    service_login_user,
    service_reset_password,
    service_signup_user,
    service_update_profile,
)

router = APIRouter(tags=["User"], redirect_slashes=False)


@router.post("/signup", response_model=UserSignupResponse)
async def router_signup_user(data: UserSignupRequest) -> UserSignupResponse:
    return await service_signup_user(data)


@router.get("/me", response_model=UserGetResponse)
async def get_current_user_me(current_user: User = Depends(get_current_user)) -> UserGetResponse:
    """
    현재 인증된 사용자 정보를 반환합니다.
    이미 get_current_user 함수가 있으므로 이를 활용하는 것이 좋습니다.
    """

    return UserGetResponse.model_validate(current_user)


@router.get("/{user_id}", response_model=UserGetResponse)
async def router_get_user(
    user_id: int,
) -> UserGetResponse:
    return await service_get_user(user_id)


@router.post("/login", response_model=UserLoginResponse)
async def router_login_user(data: UserLoginRequest) -> UserLoginResponse:
    return await service_login_user(data)


@router.post("/reset-password", response_model=UserPasswordResetResponse)
async def router_reset_password(data: UserPasswordResetRequest) -> UserPasswordResetResponse:
    return await service_reset_password(data)


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> dict[str, str]:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 혹은 비밀번호가 다릅니다.",
        )
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
    }


@router.post("/change-password", response_model=UserPasswordChangeResponse)
async def router_change_password(
    data: UserPasswordChangeRequest, current_user: User = Depends(get_current_user)
) -> UserPasswordChangeResponse:
    return await service_change_password(current_user.id, data)

@router.patch("/update-profile")
async def update_profile(
    data: UserProfileUpdateRequest, current_user: User = Depends(get_current_user)
) -> dict[str, str]:
    if data.full_name is not None:
        current_user.full_name = data.full_name
    if data.email is not None:
        current_user.email = data.email
    await current_user.save()
    return await service_update_profile(current_user.id, data)


@router.put("/{username}/set-admin", tags=["Admin"])
async def set_user_as_admin(
        username: str,
        # Tortoise ORM은 Session이나 get_db를 일반적으로 사용하지 않습니다.
        # 모델을 직접 쿼리합니다.
):
    """
    개발/테스트용: 특정 사용자의 역할을 'admin'으로 설정.
    주의: 실제 운영 시에는 이 엔드포인트에 관리자 인증/권한 체크를 반드시 추가해야 함.
    """
    db_user = await User.get_or_none(username=username)  # Tortoise ORM의 조회 방식
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # 사용자의 role 필드를 'admin'으로 변경
    db_user.role = "admin"
    await db_user.save()

    return {"message": f"User {username} is now an admin. New role: {db_user.role}"}
