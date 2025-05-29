from app.models.live_model import LiveModel
from app.models.user_model import User
from app.dtos.live.live_request import LiveStreamCreateRequest, LiveStreamUpdateRequest
from app.dtos.live.live_response import (
    LiveStreamResponse,
    AllChannelResponse,
    LiveStreamListResponse,
    StreamStartResponse,
    StreamStopResponse,
    StreamUpdateResponse,
    ChannelInfo,
)
from fastapi import HTTPException, status
import requests


async def service_start_stream(user_id: int, data: LiveStreamCreateRequest):
    """라이브 스트림 시작"""
    try:
        user = await User.get_one_by_id(user_id)

        existing_stream = await LiveModel.filter(user_id=user_id, is_active=True).first()
        if existing_stream:
            print(f"기존 스트림 발견: {existing_stream}")
            raise HTTPException (
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 활성 스트림이 있습니다."
            )

        used_channels = await LiveModel.filter(is_active=True).values_list("channel_number", flat=True)
        used_set = set(used_channels)

        channel_number = None
        for i in range(1, 17):
            if i not in used_set:
                channel_number = i
                break

        if not channel_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="모든 채널이 사용 중 입니다."
            )

        janus_room_id = 1000 + channel_number

        live_stream = await LiveModel.create(
            user=user,
            username=user.username,
            full_name=user.full_name,
            channel_number=channel_number,
            janus_room_id=janus_room_id,
            stream_title=data.stream_title,
            stream_description=data.stream_description,
            stream_category=data.stream_category,
            tags=data.tags,
            is_public=data.is_public,
            quality_setting=data.quality_setting,
        )

        return {
            "success": True,
            "message": f"채널 {channel_number}에서 스트림이 시작되었습니다.",
            "stream": {
                "channel_number": live_stream.channel_number,
                "janus_room_id": live_stream.janus_room_id,
                "stream_title": live_stream.stream_title,
                "stream_description": live_stream.stream_description,
                "stream_category": live_stream.stream_category,
                "tags": live_stream.tags,
                "is_public": live_stream.is_public,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"예상치 못한 에러: {e}")
        print(f"에러 타입: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException (
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"스트림 시작 실패: {str(e)}"
        )

# async def service_stop_stream(user_id: int) -> StreamStopResponse:
#     """라이브 스트림 종료"""
#     live_stream = await LiveModel.filter(user_id=user_id, is_active=True).first()
#
#     if not live_stream:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="항상 스트림을 찾을 수 없습니다"
#         )

async def service_stop_stream(user_id: int):
    try:
        return {"success": True, "message": "종료 성공"}
    except Exception as e:
        print(f"Stop 에러: {e}")
        return {"success": False, "message": "종료 실패"}


    # 스트림 종료
    await live_stream.stop_stream()

    return StreamStopResponse(
        success=True,
        message="스트림이 종료되었습니다.",
        duration=live_stream.duration or 0,
    )

async def service_get_all_channels() -> AllChannelResponse:
    """전체 채널 정보 조회 -> 관리자용 16채널 모니터링"""
    active_streams = await LiveModel.filter(is_active=True).all()

    channel_map = {stream.channel_number: stream for stream in active_streams}

    channels = []
    for i in range(1, 17):
        stream = channel_map.get(i)
        channel_info = ChannelInfo(
            channel_number=i,
            is_active=bool(stream.is_active),
            stream_info=LiveStreamResponse.model_validate(stream) if stream
            else None,
        )
        channels.append(channel_info)

    return AllChannelResponse(
        channels=channels,
        total_channels=16,
        active_channels=len(active_streams),
    )

# 공개 스트림 조회 => 추후
# 카테고리별 스트림 조회 => 추후

async def service_get_stream_by_channel(channel_number: int) -> LiveStreamResponse:
    """채널 번호로 스트림 조회 -> 관리자가 특정 채널 클릭 시 조회"""
    if channel_number < 1 or channel_number > 16:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    live_stream = await LiveModel.filter(
        channel_number=channel_number,
        is_active=True
    ).first()

    if not live_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"채널 {channel_number}에서 스트리밍중이 아닙니다."
        )

    return LiveStreamResponse.model_validate(live_stream)
