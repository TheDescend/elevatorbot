import os
import secrets
from datetime import timedelta
from typing import Optional

from anyio import open_file
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

# defining algorithms
from Shared.functions.helperFunctions import get_now_with_tz
from Shared.functions.readSettingsFile import get_setting

_SECRET_KEY = None
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


# get the secret key from a file if exists, otherwise generate one
async def get_secret_key():
    """Get the secret key used to create a jwt token"""

    return get_setting("SECRET")


# define auth schemes
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Make sure the hashed password is correct"""

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(plain_password: str) -> str:
    """Hash the password"""

    return pwd_context.hash(plain_password)


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a jwt token to authenticate with"""

    to_encode = data.copy()
    if expires_delta:
        expire = get_now_with_tz() + expires_delta
    else:
        expire = get_now_with_tz() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, await get_secret_key(), algorithm=ALGORITHM)
    return encoded_jwt
