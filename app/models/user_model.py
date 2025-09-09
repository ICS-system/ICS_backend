from tortoise import fields, models
from enum import Enum

from app.models.base_model import BaseModel


class UserRole(str, Enum):
    ADMIN = "admin"
    STREAMER = "streamer"


class User(BaseModel, models.Model):  # type: ignore
    username = fields.CharField(max_length=40, unique=True)
    password = fields.CharField(max_length=128)
    full_name = fields.CharField(max_length=40)
    email = fields.CharField(max_length=255, unique=True)
    agree_terms = fields.BooleanField(default=False)
    role = fields.CharEnumField(UserRole, default=UserRole.STREAMER)
    # 관리자 생성용 추가 필드
    affiliation = fields.CharField(max_length=100, null=True, description="소속")
    channel_number = fields.IntField(null=True, description="정적 할당된 채널 번호")

    @classmethod
    async def get_one_by_id(cls, user_id: int) -> "User":
        return await cls.get(id=user_id)
