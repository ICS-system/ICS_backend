from pydantic import BaseModel


class UserProfileUpdateResponse(BaseModel):
    full_name: str
    email: str
