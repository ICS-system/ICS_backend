from pydantic import BaseModel, field_validator
from typing import Optional


class AdminUserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    affiliation: Optional[str] = None
    channel_number: Optional[int] = None
    password: Optional[str] = None

    @field_validator("channel_number")
    @classmethod
    def validate_channel_range(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        if v < 1 or v > 15:
            raise ValueError("채널번호는 1-15 범위여야 합니다.")
        return v
