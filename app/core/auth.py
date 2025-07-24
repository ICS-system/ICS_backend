import os
from datetime import datetime, timedelta
from typing import Any, Optional, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from app.dtos.user.user_profile_update_request import UserProfileUpdateRequest
from app.models.user_model import User, UserRole

SECRET_KEY = os.getenv("SECRET_KEY") or ""
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # SECRET_KEY: str
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = await User.get(username=username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class RoleChecker:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="권한이 없습니다.",
            )
        return current_user

require_admin = RoleChecker([UserRole.ADMIN])
require_streamer = RoleChecker([UserRole.STREAMER])
require_any_user = RoleChecker([UserRole.ADMIN, UserRole.STREAMER])
