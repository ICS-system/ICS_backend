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

    @classmethod
    async def get_one_by_id(cls, user_id: int) -> "User":
        return await cls.get(id=user_id)
