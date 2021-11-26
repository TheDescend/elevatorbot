import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from Backend import crud
from Backend.core.security.auth import get_password_hash
from Backend.database.models import BackendUser

user_name = "auth_test"
hashed_password = get_password_hash("correct_password")
has_write_permission = True
has_read_permission = False


@pytest.mark.asyncio
async def test_authenticate(db: AsyncSession):
    test_user = BackendUser(
        user_name=user_name,
        hashed_password=hashed_password,
        has_write_permission=has_write_permission,
        has_read_permission=has_read_permission,
    )

    await crud.backend_user._insert(db, test_user)

    result = await crud.backend_user.authenticate(db, user_name, "correct_password")

    assert isinstance(result, BackendUser)


@pytest.mark.asyncio
async def test_not_authenticate(db: AsyncSession):
    result = await crud.backend_user.authenticate(db, user_name, "false_password")

    assert result is None

    result = await crud.backend_user.authenticate(db, "random_name", "correct_password")

    assert result is None
