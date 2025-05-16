from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import create_access_token, get_current_user
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

router = APIRouter(prefix="/v1/users", tags=["User"], redirect_slashes=False)


@router.post("/signup", response_model=UserSignupResponse)
async def router_signup_user(data: UserSignupRequest) -> UserSignupResponse:
    return await service_signup_user(data)


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
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/change-password", response_model=UserPasswordChangeResponse)
async def router_change_password(
    data: UserPasswordChangeRequest, current_user: User = Depends(get_current_user)
) -> UserPasswordChangeResponse:
    return await service_change_password(current_user.id, data)


@router.post("/update-profile")
async def update_profile(
    data: UserProfileUpdateRequest, current_user: User = Depends(get_current_user)
) -> dict[str, str]:
    return await service_update_profile(current_user.id, data)
