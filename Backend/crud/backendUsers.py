from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.security.auth import verify_password
from Backend.crud.base import CRUDBase
from Backend.database.models import BackendUser


class CRUDBackendUser(CRUDBase):
    async def authenticate(
        self,
        db: AsyncSession,
        user_name: str,
        password: str
    ) -> Optional[BackendUser]:
        """ Checks if the user_name has a matching pw """

        # get obj from db
        user = await self.get_with_key(db, user_name)
        if not user:
            return None

        # check pw
        if not verify_password(password, user.hashed_password):
            return None

        return user


backend_user = CRUDBackendUser(BackendUser)
