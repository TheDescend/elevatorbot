from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.security.auth import (
    ALGORITHM,
    CREDENTIALS_EXCEPTION,
    get_secret_key,
    oauth2_scheme,
)
from Backend.crud import backend_user
from Backend.database.base import get_async_session
from Backend.database.models import BackendUser


# get the database session
async def get_db_session() -> AsyncSession:
    async with get_async_session().begin() as session:
        yield session


# call this to have a function which requires an authenticated user
async def auth_get_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db_session)) -> BackendUser:
    # verify the token
    try:
        payload = jwt.decode(token, await get_secret_key(), algorithms=[ALGORITHM])
        user_name: str = payload.get("sub")
        if user_name is None:
            raise CREDENTIALS_EXCEPTION
    except JWTError:
        raise CREDENTIALS_EXCEPTION

    # get the user
    user = await backend_user._get_with_key(db, user_name)

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
async def auth_get_user_with_read_perm(
    user: BackendUser = Depends(auth_get_user),
) -> BackendUser:
    if not user.has_read_permission:
        raise HTTPException(status_code=400, detail="Read permissions are missing")
    return user


# call this to have a function which requires write permissions
async def auth_get_user_with_write_perm(
    user: BackendUser = Depends(auth_get_user),
) -> BackendUser:
    if not user.has_write_permission:
        raise HTTPException(status_code=400, detail="Write permissions are missing")
    return user
