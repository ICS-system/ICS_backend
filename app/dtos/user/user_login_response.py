from pydantic import BaseModel

from app.models.user_model import User


class UserLoginResponse(BaseModel):
    user_id: int
    username: str
    full_name: str
    email: str


async def to_user_login_response(user: User) -> UserLoginResponse:
    return UserLoginResponse(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
    )
