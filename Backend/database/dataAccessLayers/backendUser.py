from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from Backend.database.models import BackendUser


class BackendUserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session


    async def get_user(
        self,
        user_name: str
    ) -> Optional[BackendUser]:
        res = await self.db_session.get(BackendUser, user_name)
        return res


    async def create_user(
        self,
        user_name: str,
        hashed_password: str,
        allowed_scopes: list[str],
        has_write_permission: bool,
        has_read_permission: bool,
    ) -> BackendUser:
        new_user = BackendUser(
            user_name=user_name,
            hashed_password=hashed_password,
            allowed_scopes=allowed_scopes,
            has_write_permission=has_write_permission,
            has_read_permission=has_read_permission,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user


    async def update_user(
        self,
        user_name: str,
        hashed_password: Optional[str],
        allowed_scopes: Optional[list[str]],
        has_write_permission: Optional[bool],
        has_read_permission: Optional[bool],
        disabled: Optional[bool]
    ) -> Result:
        query = update(BackendUser).where(BackendUser.user_name == user_name)

        if hashed_password:
            query = query.values(hashed_password=hashed_password)
        if allowed_scopes:
            query = query.values(allowed_scopes=allowed_scopes)
        if has_write_permission:
            query = query.values(has_write_permission=has_write_permission)
        if has_read_permission:
            query = query.values(has_read_permission=has_read_permission)
        if disabled:
            query = query.values(disabled=disabled)

        query.execution_options(synchronize_session="fetch")
        return await self.db_session.execute(query)
