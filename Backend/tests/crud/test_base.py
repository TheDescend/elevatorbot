from copy import copy

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from Backend import crud
from Backend.core.security.auth import get_password_hash
from Backend.database.models import BackendUser

user_name = "test"
user_name2 = "test2"
hashed_password = get_password_hash("test")
allowed_scopes = ["here", "also here"]
has_write_permission = True
has_read_permission = False

test_user = BackendUser(
    user_name=user_name,
    hashed_password=hashed_password,
    allowed_scopes=allowed_scopes,
    has_write_permission=has_write_permission,
    has_read_permission=has_read_permission,
)
test_user2 = BackendUser(
    user_name=user_name2,
    hashed_password=hashed_password,
    allowed_scopes=allowed_scopes,
    has_write_permission=has_write_permission,
    has_read_permission=has_read_permission,
)


# first, lets test the crud base backendNetworking, so they do not have to be retested for every item
# if they dont get overloaded at least
# using BackendUser for that
@pytest.mark.asyncio
async def test_insert_and_get(db: AsyncSession):
    await crud.backend_user._insert(db, test_user)
    result = await crud.backend_user._get_with_key(db, user_name)

    assert isinstance(result, BackendUser)
    assert result.user_name == user_name
    assert isinstance(result.allowed_scopes, list)

    await crud.backend_user._insert(db, test_user2)
    result = await crud.backend_user._get_with_key(db, user_name2)

    assert isinstance(result, BackendUser)
    assert result.user_name == user_name2


@pytest.mark.asyncio
async def test_update(db: AsyncSession):
    await crud.backend_user._insert(db, test_user)

    assert test_user.has_write_permission

    await crud.backend_user._update(db, test_user, has_write_permission=False)

    result = await crud.backend_user._get_with_key(db, user_name)

    assert not result.has_write_permission


@pytest.mark.asyncio
async def test_get_multi(db: AsyncSession):
    await crud.backend_user._insert(db, test_user)
    await crud.backend_user._insert(db, test_user2)

    results = await crud.backend_user._get_all(db)

    assert isinstance(results, list)
    assert results

    assert test_user in results
    assert test_user2 in results


@pytest.mark.asyncio
async def test_get_multi_with_column(db: AsyncSession):
    await crud.backend_user._insert(db, test_user)
    await crud.backend_user._insert(db, test_user2)

    results = await crud.backend_user._get_multi(db, has_read_permission=has_read_permission)

    assert isinstance(results, list)
    assert results
    assert len(results) > 1

    assert test_user in results
    assert test_user2 in results


@pytest.mark.asyncio
async def test_remove(db: AsyncSession):
    result = await crud.backend_user._delete(db, user_name)

    assert isinstance(result, BackendUser)

    result = await crud.backend_user._get_with_key(db, user_name)

    assert result is None

    results = await crud.backend_user._get_all(db)
    assert test_user not in results
