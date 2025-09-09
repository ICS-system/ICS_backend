from string import ascii_lowercase

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt

from app.core.auth import create_access_token, get_current_user, oauth2_scheme, ALGORITHM, SECRET_KEY, require_admin
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
from app.dtos.user.user_signup_response import UserGetResponse, UserSignupResponse, StreamerListItem, StreamerListResponse
from app.dtos.user.admin_user_add_request import AdminUserAddRequest
from app.dtos.user.admin_user_update_channel_request import AdminUserUpdateRequest
from app.models.user_model import User
from app.services.user_service import (
    authenticate_user,
    service_change_password,
    service_get_user,
    service_login_user,
    service_reset_password,
    service_signup_user,
    service_update_profile,
    service_admin_add_user,
    service_admin_delete_user,
    service_admin_update_user,
    service_admin_list_streamers,
)

router = APIRouter(tags=["User"], redirect_slashes=False)


# Admin 전용 사용자 생성 API (정적 채널 부여, 이메일 없이 지정)
@router.post("/add_user", response_model=UserSignupResponse, tags=["Admin"], dependencies=[Depends(require_admin)])
async def admin_add_user(data: AdminUserAddRequest) -> UserSignupResponse:
    return await service_admin_add_user(data)


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


@router.put("/{username}/set-admin", tags=["Admin"], dependencies=[Depends(require_admin)])
async def set_user_as_admin(username: str):
    """
    개발/테스트용: 특정 사용자의 역할을 'admin'으로 설정.
    """
    db_user = await User.get_or_none(username=username)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db_user.role = "admin"
    await db_user.save()

    return {"message": f"User {username} is now an admin. New role: {db_user.role}"}


# Admin: 사용자 삭제
@router.delete("/{username}", tags=["Admin"], dependencies=[Depends(require_admin)])
async def admin_delete_user(username: str) -> dict[str, str]:
    return await service_admin_delete_user(username)


# Admin: 사용자 정보 변경 (이름/소속/채널/비밀번호)
@router.patch("/{username}", tags=["Admin"], dependencies=[Depends(require_admin)])
async def admin_update_user(username: str, data: AdminUserUpdateRequest) -> dict[str, str]:
    return await service_admin_update_user(username, data)


# Admin: 스트리머 목록 조회 (채널/소속/이름 포함)
@router.get("/streamers", response_model=StreamerListResponse, tags=["Admin"], dependencies=[Depends(require_admin)])
async def admin_list_streamers() -> StreamerListResponse:
    return await service_admin_list_streamers()
