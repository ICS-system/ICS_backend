from pydantic import BaseModel, Field
from typing import Optional, List


class LiveStreamCreateRequest(BaseModel):
    """라이브 스트림 생성 요청"""
    stream_title: str
    stream_description: str
    stream_category: str
    tags: List[str]
    is_public: bool
    quality_setting: str


class LiveStreamUpdateRequest(BaseModel):
    """라이브 스트림 정보 수정 요청"""
    stream_title: str
    stream_description: str
    stream_category: str
    tags: List[str]
    is_public: bool
    quality_setting: str


class StreamCategoryRequest(BaseModel):
    """카테고리별 스트림 조회 요청"""
    category: str