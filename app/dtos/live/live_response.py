from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class LiveStreamResponse(BaseModel):
    """라이브 스트림 응답"""
    id: int
    user_id: int
    username: str
    full_name: str
    channel_number: int
    janus_room_id: Optional[int] = None
    stream_category: str
    stream_title: str
    stream_description: Optional[str] = None
    tags: List[str]
    thumbnail_url: Optional[str]
    is_public: bool
    quality_setting: str
    is_active: bool
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration: Optional[int] = None
    created_at: datetime
    modified_at: datetime
    hls_url: Optional[str] = None  # CCTV HLS 스트림 URL

    class Config:
        from_attributes = True


class ChannelInfo(BaseModel):
    """채널 정보"""
    channel_number: int
    is_active: bool
    stream_info: Optional[LiveStreamResponse] = None


class AllChannelResponse(BaseModel):
    """전체 채널 정보 응답"""
    channels: List[ChannelInfo]
    total_channels: int
    active_channels: int


class LiveStreamListResponse(BaseModel):
    """라이브 스트림 목록 응답"""
    streams: List[LiveStreamResponse]
    total_count: int


class StreamStartResponse(BaseModel):
    """스트림 시작 응답"""
    success: bool
    message: str
    stream: LiveStreamResponse


class StreamStopResponse(BaseModel):
    """스트림 종료 응답"""
    success: bool
    message: str
    duration: int


class StreamUpdateResponse(BaseModel):
    """스트림 업데이트 응답"""
    success: bool
    message: str
    stream: LiveStreamResponse


class ErrorResponse(BaseModel):
    """에러 응답"""
    success: bool
    error_code: str
    message: str
    details: str
