from pydantic import BaseModel


class UserSignupRequest(BaseModel):
    username: str
    password: str
    full_name: str
    email: str
    affiliation: str | None = None
    channel_number: int | None = None


class UserGetRequest(BaseModel):
    username: str
    full_name: str
    email: str
