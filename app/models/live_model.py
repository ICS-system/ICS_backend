from tortoise import fields, models
from app.models.base_model import BaseModel
from typing import Optional, List
from datetime import datetime


class LiveModel(BaseModel, models.Model):  # type: ignore
    """라이브 스트림 모델"""

    username = fields.CharField(max_length=50, index=True, description="스트리머 사용자명")
    full_name = fields.CharField(max_length=100, description="스트리머 실명")
    channel_number = fields.IntField(index=True, description="채널 번호 (1-16)")
    janus_room_id = fields.IntField(description="Janus room ID")

    stream_category = fields.CharField(max_length=50, default="일반")
    stream_title = fields.CharField(max_length=200, default="라이브 스트림", description="스트림 제목")
    stream_description = fields.TextField(null=True)

    tags = fields.JSONField(default=list)
    thumbnail_url = fields.CharField(max_length=500, null=True)

    is_public = fields.BooleanField(default=True)
    quality_setting = fields.CharField(max_length=20, default="HD")

    is_active = fields.BooleanField(default=True, description="스트림 활성 상태")
    started_at = fields.DatetimeField(auto_now_add=True, description="스트림 시작 시간")
    ended_at = fields.DatetimeField(null=True, description="스트림 종료 시간")
    user = fields.ForeignKeyField("models.User", related_name="live_streams", null=True)

    class Meta:
        table = "lives"
        table_description = "라이브 스트림 정보"
        indexes = [
            ("channel_number", "is_active"),
            ("janus_room_id",),
            ("user_id", "is_active"),
            ("started_at",)
        ]
        ordering = ["-started_at"]
        unique_together = ("user", "is_active")

    def __str__(self) -> str:
        return f"Live(id={self.id}, user={self.username}, channel={self.channel_number})"

    @classmethod
    async def get_streams_by_category(cls, category: str) -> List["LiveModel"]:
        """카테고리별 스트림 조회"""
        return await cls.filter(
            is_active=True,
            stream_category=category,
        ).order_by("-started_at")

    @classmethod
    async def get_public_streams(cls) -> List["LiveModel"]:
        """공개 스트림만 조회"""
        return await cls.filter(
            is_public=True,
            is_active=True,
        ).order_by("channel_number")

    @classmethod
    async def get_recent_streams(cls) -> List["LiveModel"]:
        """최근 스트림 순으로 조회"""
        return await cls.filter(is_active=True).order_by("-started_at")

    @classmethod
    async def get_streams_by_duration(cls) -> List["LiveModel"]:
        """오래 진행된 스트림 순으로 조회"""
        return await cls.filter(is_active=True).order_by("started_at")

    @classmethod
    async def get_one_by_id(cls, live_id: int) -> "LiveModel":
        """ID로 라이브 스트림 조회 (User 모델과 일관성)"""
        return await cls.get(id=live_id)

    @classmethod
    async def get_by_janus_room_id(cls, room_id: int) -> Optional["LiveModel"]:
        """Janus 방 ID로 라이브 스트림 조회"""
        return await cls.filter(janus_room_id=room_id, is_active=True).first()

    async def stop_stream(self):
        """스트림 종료"""
        self.is_active = False
        self.ended_at = datetime.now()
        await self.save()

    async def update_stream_info(self, stream_title: str = None):
        """스트림 정보 업데이트"""
        if stream_title:
            self.stream_title = stream_title
        await self.save()

    @property
    def duration(self) -> Optional[int]:
        """스트림 지속 시간 (초 단위)"""
        if self.ended_at:
            return int((self.ended_at - self.started_at).total_seconds())
        elif self.is_active:
            return int((datetime.now() - self.started_at).total_seconds())
        return None
