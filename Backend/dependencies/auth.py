from datetime import datetime, timedelta
from typing import Optional
import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from passlib.context import CryptContext
from jose import JWTError, jwt

from Backend.database.dataAccessLayers.backendUser import BackendUserDAL
from Backend.database.models import BackendUser

# defining algorithms
from Backend.dependencies.databaseObjects import get_backend_user
from Backend.schemas.auth import TokenData


_SECRET_KEY = None
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={
        "WWW-Authenticate": "Bearer"
    },
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


async def authenticate_user(user: Optional[BackendUser], password: str) -> bool:
    if user is None:
        return False

    if not verify_password(password, user.hashed_password):
        return False

    return True


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm=ALGORITHM)
    return encoded_jwt


async def auth_get_user(token: str = Depends(oauth2_scheme), user_dal: BackendUserDAL = Depends(get_backend_user)):
    # verify the token
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise CREDENTIALS_EXCEPTION
        token_data = TokenData(username=username)
    except JWTError:
        raise CREDENTIALS_EXCEPTION

    # get the user
    user = await user_dal.get_user(user_name=token_data.username)

    # verify that the user is OK
    if user is None:
        raise CREDENTIALS_EXCEPTION
    elif user.disabled:
        raise HTTPException(
            status_code=400,
            detail="This user account has been disabled",
        )

    return user


# call this to have a function which requires read permissions
async def auth_get_user_with_read_perm(user: BackendUser = Depends(auth_get_user)):
    if not user.has_read_permission:
        raise HTTPException(status_code=400, detail="Read permissions are missing")
    return user


# call this to have a function which requires write permissions
async def auth_get_user_with_write_perm(user: BackendUser = Depends(auth_get_user)):
    if not user.has_write_permission:
        raise HTTPException(status_code=400, detail="Write permissions are missing")
    return user
