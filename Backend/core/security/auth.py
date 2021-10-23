import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from Backend.database.models import BackendUser

# defining algorithms
from Backend.misc.helperFunctions import get_now_with_tz

_SECRET_KEY = None
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


# get the secret key from a file if exists, otherwise generate one
def get_secret_key():
    global _SECRET_KEY

    if not _SECRET_KEY:
        secrets_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "secrets.py")
        if os.path.exists(secrets_file_path):
            with open(secrets_file_path, "r") as file:
                secret_key = file.read()
        else:
            with open(secrets_file_path, "w+") as file:
                secret_key = secrets.token_hex()
                file.write(secret_key)
        _SECRET_KEY = secret_key

    return _SECRET_KEY


# define auth schemes
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = get_now_with_tz() + expires_delta
    else:
        expire = get_now_with_tz() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm=ALGORITHM)
    return encoded_jwt
