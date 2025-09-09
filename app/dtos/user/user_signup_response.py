from pydantic import BaseModel, ConfigDict

from app.models.user_model import User


class UserSignupResponse(BaseModel):
    user_id: int
    username: str
    full_name: str
    email: str
    affiliation: str | None = None
    channel_number: int | None = None


async def to_user_signup_response(user: User) -> UserSignupResponse:
    return UserSignupResponse(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        affiliation=user.affiliation,
        channel_number=user.channel_number,
    )


class UserGetResponse(BaseModel):
    id: int
    username: str
    full_name: str
    email: str
    affiliation: str | None = None
    channel_number: int | None = None

    model_config = ConfigDict(from_attributes=True)

async def to_user_get_response(user: User) -> UserGetResponse:
    return UserGetResponse.from_orm(user)


class StreamerListItem(BaseModel):
    username: str
    full_name: str
    affiliation: str | None = None
    channel_number: int | None = None


class StreamerListResponse(BaseModel):
    items: list[StreamerListItem]
