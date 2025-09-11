from tortoise.exceptions import IntegrityError

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
from datetime import datetime, timezone
from asyncio import Lock
from tortoise.transactions import in_transaction
import asyncio
import random


# 어플리케이션 레벨 Lock
channel_allocation_lock = Lock()


async def service_start_stream(user_id: int, data: LiveStreamCreateRequest):
    """라이브 스트림 시작 (이중 Lock 적용 추가)"""
    try:
        # 애플리케이션 레벨 동시성 제어
        async with channel_allocation_lock:
            print(f"[{user_id}] 채널 할당 Lock 획득")

            # 재시도 로직 추가
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # 데이터 베이스 트랜잭션 보호
                    async with in_transaction() as connection:
                        print(f"[{user_id}] 데이터베이스 트랜잭션 시작 (시도 {attempt + 1})")

                        user = await User.get_one_by_id(user_id)

                        # 기존 스트림 종료
                        existing_streams = await LiveModel.filter(user_id=user_id, is_active=True)
                        if existing_streams:
                            print(f"기존 스트림 종료: {existing_streams}")
                            print(f"[{user_id}] 기존 스트림 삭제: {len(existing_streams)}개")
                            await LiveModel.filter(user_id=user_id, is_active=True).delete()

                        # 최소한의 트랜잭션(DB 작업만)
                        async with in_transaction():
                            print(f"[{user_id}] 최소 트랜잭션 시작")

                            # 사용 중인 채널 확인
                            used_channels = await LiveModel.filter(is_active=True).values_list("channel_number", flat=True)
                            used_set = set(used_channels)
                            print(f"[{user_id}] 사용 중인 채널: {used_set}")


                            # 사용 가능한 채널 (1~15만 할당, 16번은 신고자 전용)
                            channel_number = None
                            for i in range(1, 16):
                                if i not in used_set:
                                    channel_number = i
                                    break

                            if not channel_number:
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="모든 스트리머 채널(1~15)이 사용 중 입니다."
                                )

                            janus_room_id = 1002
                            print(f"할당된 채널: {channel_number}, room_id: {janus_room_id}")

                            # 유니크 제약 조건 회피
                            existing_channel = await LiveModel.filter(channel_number=channel_number, is_active=True).first()

                            if existing_channel:
                                print(f"[{user_id}] 채널 {channel_number} 이미 사용 중, 재시도")

                                continue

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

                            print(f"[{user_id}] 스트림 생성 완료 - 채널 {channel_number}")

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

                except IntegrityError as e:
                    if "Duplicate entry" in str(e) and attempt < max_retries - 1:
                        print(f"[{user_id}] 유니크 제약 조건 위반, 재시도 {attempt + 1}")
                        await asyncio.sleep(0.1 * (attempt + 1))
                        continue
                    else:
                        raise e

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="채널 할당 중 충돌이 발생했습니다. 잠시 후 기다려주세요."
            )

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

async def service_stop_stream(user_id: int):
    """라이브 스트림 종료 - 트랜잭션 적용"""
    try:
        async with in_transaction():
            live_stream = await LiveModel.filter(user_id=user_id, is_active=True).first()

            if not live_stream:
                return {"success": False, "message": "활성 스트림이 없습니다."}

            # 스트림 종료
            live_stream.is_active = False
            live_stream.ended_at = datetime.now(timezone.utc)
            await live_stream.save()

            print(f"[{user_id}] 채널 {live_stream.channel_number} 스트림 종료 완료")

            return StreamStopResponse(
                success=True,
                message="스트림이 종료되었습니다.",
                duration=live_stream.duration or 0,
            )

    except Exception as e:
        print(f"Stop 에러: {e}")
        return {"success": False, "message": f"종료 실패: {str(e)}"}


async def get_available_room_id() -> int:
    """사용 가능한 room_id 찾기"""
    used_room_ids = await LiveModel.all().values_list("janus_room_id", flat=True)
    used_set = set(used_room_ids)

    for room_id in range(1001, 10000):
        if room_id not in used_set:
            return room_id


async def service_get_all_channels() -> AllChannelResponse:
    """전체 채널 정보 조회 -> 관리자용 16채널 모니터링"""
    try:
        active_streams = await LiveModel.filter(is_active=True).all()

        channel_map = {stream.channel_number: stream for stream in active_streams}

        channels = []
        for i in range(1, 17):
            stream = channel_map.get(i)

            try:
                if stream:
                    stream_info = LiveStreamResponse.model_validate(stream)

                    channel_info = ChannelInfo(
                        channel_number=i,
                        is_active=True,
                        stream_info=stream_info,
                    )
                else:
                    channel_info = ChannelInfo(
                        channel_number=i,
                        is_active=False,
                        stream_info=None,
                    )

            except Exception as e:
                print(f"채널 {i} 처리 중 오류: {e}")
                channel_info = ChannelInfo(
                    channel_number=i,
                    is_active=False,
                    stream_info=None,
                )

            channels.append(channel_info)

        return AllChannelResponse(
            channels=channels,
            total_channels=16,
            active_channels=len(active_streams),
        )

    except Exception as e:
        print(f"service_get_all_channels 전체 오류: {e}")
        import traceback
        traceback.print_exc()
        raise


# 공개 스트림 조회 => 추후
# 카테고리별 스트림 조회 => 추후

async def service_get_stream_by_channel(channel_number: int) -> LiveStreamResponse:
    """채널 번호로 스트림 조회 -> 관리자가 특정 채널 클릭 시 조회"""
    if channel_number < 1 or channel_number > 16:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="잘못된 채널 번호입니다."
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
