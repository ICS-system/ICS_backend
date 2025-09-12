from string import ascii_lowercase
from typing import Optional

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
from app.dtos.user.user_signup_response import UserGetResponse, UserSignupResponse, StreamerListItem, StreamerListResponse, UserListItem, UserListResponse
from app.dtos.user.admin_user_add_request import AdminUserAddRequest
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
    service_admin_list_streamers,
    service_admin_list_all_users,
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


# Admin: 모든 사용자 목록 조회 (관리자 + 스트리머) - /{user_id}보다 먼저 정의
@router.get("/all", response_model=UserListResponse, tags=["Admin"], dependencies=[Depends(require_admin)])
async def admin_list_all_users() -> UserListResponse:
    return await service_admin_list_all_users()


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




# Admin: 스트리머 목록 조회 (채널/소속/이름 포함)
@router.get("/streamers", response_model=StreamerListResponse, tags=["Admin"], dependencies=[Depends(require_admin)])
async def admin_list_streamers() -> StreamerListResponse:
    return await service_admin_list_streamers()


# ========== Admin: 사용자 관리 API ==========
@router.get("/management/users", tags=["Admin"], dependencies=[Depends(require_admin)])
async def get_all_users(
    affiliation: Optional[str] = None,  # 소속별 필터링
    current_user: User = Depends(get_current_user)
):
    """모든 사용자 목록 조회 (소속별 필터링 가능)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자만 접근 가능")
    
    query = User.all()
    if affiliation:
        query = query.filter(affiliation=affiliation)
    
    users = await query.order_by('username')
    
    # 프론트엔드 요구사항에 맞게 응답 형식 변경
    user_list = []
    for user in users:
        user_data = {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "affiliation": user.affiliation,
            "role": user.role,
            "channel_number": user.channel_number,
            "is_channel_assigned": user.is_channel_assigned
        }
        user_list.append(user_data)
    
    return {"users": user_list}

@router.put("/management/users/{user_id}", tags=["Admin"], dependencies=[Depends(require_admin)])
async def update_user(
    user_id: int,
    user_data: dict,  # 임시로 dict 사용, 나중에 DTO로 변경
    current_user: User = Depends(get_current_user)
):
    """사용자 정보 수정 (이름, 비밀번호, 소속 등)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자만 접근 가능")
    
    user = await User.get(id=user_id)
    
    # 사용자 정보 업데이트
    if "full_name" in user_data:
        user.full_name = user_data["full_name"]
    if "affiliation" in user_data:
        user.affiliation = user_data["affiliation"]
    if "email" in user_data:
        user.email = user_data["email"]
    
    await user.save()
    return {"message": "사용자 정보가 수정되었습니다"}

@router.delete("/management/users/{user_id}", tags=["Admin"], dependencies=[Depends(require_admin)])
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """사용자 삭제"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자만 접근 가능")
    
    user = await User.get(id=user_id)
    await user.delete()
    return {"message": "사용자가 삭제되었습니다"}

@router.put("/management/users/{user_id}/set-admin", tags=["Admin"], dependencies=[Depends(require_admin)])
async def set_user_as_admin(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """사용자를 관리자로 설정"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자만 접근 가능")
    
    user = await User.get(id=user_id)
    user.role = "admin"
    await user.save()
    
    return {"message": f"{user.username}이 관리자로 설정되었습니다"}


