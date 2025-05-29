from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from app.core.auth import get_current_user
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


# ========== RESTful 스트림 관리 (새로 추가) ==========

@router.post("/streams", response_model=StreamStartResponse)
async def create_stream(
        data: LiveStreamCreateRequest,
        current_user: User = Depends(get_current_user),
) -> StreamStartResponse:
    """스트림 생성"""
    return await service_start_stream(current_user.id, data)

@router.delete("/streams/current", response_model=StreamStopResponse)
async def delete_current_stream(
        current_user: User = Depends(get_current_user),
) -> StreamStopResponse:
    """현재 사용자의 활성 스트림 삭제"""
    return await service_stop_stream(current_user.id)


@router.get("/channels", response_model=AllChannelResponse)
async def list_channels() -> AllChannelResponse:
    """전체 채널 목록"""
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

@router.post("/start")
async def router_start_stream(
        data: LiveStreamCreateRequest,
        current_user: User = Depends(get_current_user),
):
    """라이브 스트림 시작"""
    return await service_start_stream(current_user.id, data)

@router.post("/stop")
async def router_stop_stream(
        current_user: User = Depends(get_current_user),
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
