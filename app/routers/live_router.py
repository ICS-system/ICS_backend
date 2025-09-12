from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from datetime import datetime, timedelta

from app.core.auth import get_current_user, require_admin, require_streamer, require_any_user
from app.dtos.live.live_request import (
    LiveStreamCreateRequest,
    LiveStreamUpdateRequest,
)
from app.dtos.live.live_response import (
    LiveStreamResponse,
    AllChannelResponse,
    StreamStartResponse,
    StreamStopResponse,
    StreamUpdateResponse,
    LiveStreamListResponse,
)
from app.models.user_model import User
from app.services.live_service import (
    service_start_stream,
    service_stop_stream,
    service_get_all_channels,
    service_get_stream_by_channel,
)

router = APIRouter(prefix="/v1/live", tags=["live"], redirect_slashes=False)


@router.post("/streams", response_model=StreamStartResponse, dependencies=[Depends(require_streamer)])
async def create_stream(
        data: LiveStreamCreateRequest,
        current_user: User = Depends(require_streamer),
) -> StreamStartResponse:
    """스트림 생성"""
    return await service_start_stream(current_user.id, data)

@router.delete("/streams/current", response_model=StreamStopResponse)
async def delete_current_stream(
        current_user: User = Depends(require_streamer),
) -> StreamStopResponse:
    """현재 사용자의 활성 스트림 삭제"""
    return await service_stop_stream(current_user.id)


@router.get("/channels", response_model=AllChannelResponse, dependencies=[Depends(require_any_user)])
async def list_channels(current_user = Depends(require_any_user)) -> AllChannelResponse:
    """전체 채널 목록"""
    return await service_get_all_channels()


@router.get("/admin/channels", dependencies=[Depends(require_admin)])
async def get_all_channels_admin(current_user = Depends(require_admin)) -> AllChannelResponse:
    """관리자 전용: 전체 채널 모니터링"""
    return await service_get_all_channels()


@router.get("/channels/{channel_number}", response_model=LiveStreamResponse)
async def get_channel(channel_number: int) -> LiveStreamResponse:
    """특정 채널 조회"""
    return await service_get_stream_by_channel(channel_number)

# ==========스트림 조회==========

@router.get("/streams", response_model=LiveStreamListResponse)
async def list_streams(
    category: Optional[str] = Query(None, description="카테고리 필터"),
    public: Optional[bool] = Query(None, description="공개 여부 필터"),
    limit: int = Query(50, ge=1, le=100, description="결과 수 제한"),
    offset: int = Query(0, ge=0, description="결과 오프셋")
) -> LiveStreamListResponse:
    """스트림 목록 조회 (쿼리 파라미터로 필터링)"""
    if category:
        return await service_get_streams_by_category(category)
    elif public is True:
        return await service_get_public_streams()
    else:
        # 전체 스트림 조회 (새 서비스 함수 필요)
        return await service_get_all_streams(limit, offset)

@router.post("/start", response_model=StreamStartResponse)
async def router_start_stream(
        data: LiveStreamCreateRequest,
        current_user: User = Depends(require_streamer),
):
    """라이브 스트림 시작"""
    return await service_start_stream(current_user.id, data)

@router.post("/stop", response_model=StreamStopResponse)
async def router_stop_stream(
        current_user: User = Depends(require_streamer),
):
    """라이브 스트림 종료"""
    return await service_stop_stream(current_user.id)

@router.patch("/update", response_model=StreamUpdateResponse)
async def router_update_stream(
        data: LiveStreamUpdateRequest,
        current_user: User = Depends(get_current_user),
) -> StreamUpdateResponse:
    """라이브 스트림 정보 수정"""
    return await service_update_stream(current_user.id, data)


@router.get("/public", response_model=LiveStreamListResponse)
async def router_get_public_streams() -> LiveStreamListResponse:
    """공개 스트림 목록 조회"""
    return await service_get_public_streams()

@router.get("/category/{category}", response_model=LiveStreamListResponse)
async def router_get_streams_by_category(category: str) -> LiveStreamListResponse:
    """카테고리별 스트림 조회"""
    return await service_get_streams_by_category(category)

@router.get("/channel/{channel_number}", response_model=LiveStreamResponse)
async def router_get_stream_by_channel(channel_number: int) -> LiveStreamResponse:
    """채널명 스트림 조회 - 관리자가 특정 채널 클릭 시 개별 조회"""
    return await service_get_stream_by_channel(channel_number)


# ========== 신고자 채널 16 관리 ==========
@router.post("/management/channels/16/token", tags=["Admin"], dependencies=[Depends(require_admin)])
async def create_reporter_token(
    token_data: dict,  # 임시로 dict 사용, 나중에 DTO로 변경
    current_user: User = Depends(get_current_user)
):
    """신고자용 유효토큰 생성 (채널 16)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자만 접근 가능")
    
    # 유효시간 설정 (1시간, 3시간 등)
    valid_hours = token_data.get("valid_hours", 1)
    expires_at = datetime.now() + timedelta(hours=valid_hours)
    
    # 보안 토큰 생성 (secrets 사용)
    from app.services.token_service import token_service
    token = token_service.generate_secure_token()
    
    # Redis에 토큰 정보 저장
    await token_service.save_reporter_token(
        token=token,
        expires_at=expires_at,
        valid_hours=valid_hours,
        created_by=current_user.username
    )
    
    # URL 생성
    reporter_url = f"https://hanswell.app/reporter/{token}"
    
    return {
        "token": token,
        "url": reporter_url,
        "expires_at": expires_at.isoformat(),
        "valid_hours": valid_hours
    }

@router.get("/report/validate/{token}", tags=["Public"])
async def validate_reporter_token(token: str):
    """신고자 토큰 검증"""
    from app.services.token_service import token_service
    
    token_data = await token_service.validate_reporter_token(token)
    
    if not token_data:
        raise HTTPException(status_code=404, detail="유효하지 않은 토큰입니다")
    
    if token_data.get("is_used", False):
        raise HTTPException(status_code=400, detail="이미 사용된 토큰입니다")
    
    return {
        "valid": True,
        "expires_at": token_data["expires_at"],
        "valid_hours": token_data["valid_hours"]
    }

@router.post("/report/access/{token}", tags=["Public"])
async def access_reporter_channel(token: str):
    """신고자 채널 접근"""
    from app.services.token_service import token_service
    
    token_data = await token_service.validate_reporter_token(token)
    
    if not token_data:
        raise HTTPException(status_code=404, detail="유효하지 않은 토큰입니다")
    
    if token_data.get("is_used", False):
        raise HTTPException(status_code=400, detail="이미 사용된 토큰입니다")
    
    # 토큰 사용 완료 표시
    await token_service.mark_token_as_used(token)
    
    return {
        "message": "채널 16에 접근이 허용되었습니다",
        "channel_number": 16,
        "janus_room_id": 1002
    }
