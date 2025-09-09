from pydantic import BaseModel, field_validator


class AdminUserAddRequest(BaseModel):
    username: str
    password: str
    full_name: str
    affiliation: str
    channel_number: int

    @field_validator("channel_number")
    @classmethod
    def validate_channel_range(cls, v: int) -> int:
        if v < 1 or v > 15:
            raise ValueError("채널번호는 1-15 범위여야 합니다.")
        return v
