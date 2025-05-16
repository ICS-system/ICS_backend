from pydantic import BaseModel


class UserProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    email: str | None = None
