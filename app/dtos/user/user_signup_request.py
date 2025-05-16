from pydantic import BaseModel


class UserSignupRequest(BaseModel):
    username: str
    password: str
    full_name: str
    email: str


class UserGetRequest(BaseModel):
    username: str
    full_name: str
    email: str
