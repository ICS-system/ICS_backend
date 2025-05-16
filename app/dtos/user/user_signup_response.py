from pydantic import BaseModel

from app.models.user_model import User


class UserSignupResponse(BaseModel):
    user_id: int
    username: str
    full_name: str
    email: str


async def to_user_signup_response(user: User) -> UserSignupResponse:
    return UserSignupResponse(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
    )


class UserGetResponse(BaseModel):
    user_id: int
    username: str
    full_name: str
    email: str


async def to_user_get_response(user: User) -> UserGetResponse:
    return UserGetResponse(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
    )
