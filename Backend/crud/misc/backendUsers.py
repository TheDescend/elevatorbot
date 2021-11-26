from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.security.auth import get_password_hash, verify_password
from Backend.crud.base import CRUDBase
from Backend.database.models import BackendUser
from settings import ADMIN_PASSWORD


class CRUDBackendUser(CRUDBase):
    async def authenticate(self, db: AsyncSession, user_name: str, password: str) -> Optional[BackendUser]:
        """Checks if the user_name has a matching pw"""

        # get obj from db
        user = await self._get_with_key(db, user_name)
        if not user:
            return None

        # check pw
        if not verify_password(password, user.hashed_password):
            return None

        return user

    async def create_admin(self, db: AsyncSession) -> BackendUser:
        """Create the account used by the website to access my data"""

        user_name = "admin"
        model = await self._get_with_key(db=db, primary_key=user_name)

        # only insert if not exists yet
        if not model:
            model = BackendUser(
                user_name="admin",
                hashed_password=get_password_hash(ADMIN_PASSWORD),
                has_write_permission=True,
                has_read_permission=True,
                disabled=False,
            )
            await self._insert(db=db, to_create=model)
        return model


backend_user = CRUDBackendUser(BackendUser)
