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
test_user2 = copy(test_user)
test_user2.user_name = user_name2


# first, lets test the crud base functions, so they do not have to be retested for every item
# if they dont get overloaded at least
# using BackendUser for that
@pytest.mark.asyncio
async def test_insert_and_get(
    db: AsyncSession
):
    await crud.backend_user.insert(db, copy(test_user))
    result = await crud.backend_user.get_with_key(db, user_name)

    assert isinstance(result, BackendUser)
    assert result.user_name == user_name
    assert isinstance(result.allowed_scopes, list)

    await crud.backend_user.insert(db, copy(test_user2))
    result = await crud.backend_user.get_with_key(db, user_name2)

    assert isinstance(result, BackendUser)
    assert result.user_name == user_name2


@pytest.mark.asyncio
async def test_update(
    db: AsyncSession
):
    result = await crud.backend_user.get_with_key(db, user_name2)

    assert result.has_write_permission

    test_user2_updated = copy(test_user2)
    test_user2_updated.has_write_permission = False
    await crud.backend_user.insert(db, test_user2_updated)

    result = await crud.backend_user.get_with_key(db, user_name2)

    assert not result.has_write_permission


@pytest.mark.asyncio
async def test_get_multi(
    db: AsyncSession
):
    results = await crud.backend_user.get_multi(db)

    assert isinstance(results, list)
    assert results

    for result in results:
        assert isinstance(result, BackendUser)


@pytest.mark.asyncio
async def test_get_multi(
    db: AsyncSession
):
    results = await crud.backend_user.get_multi_with_column(db, column_name="hashed_password", column_value=hashed_password)

    assert isinstance(results, list)
    assert results

    for result in results:
        assert isinstance(result, BackendUser)


@pytest.mark.asyncio
async def test_remove(
    db: AsyncSession
):
    result = await crud.backend_user.delete(db, user_name)

    assert isinstance(result, BackendUser)

    result = await crud.backend_user.get_with_key(db, user_name)

    assert result is None

    results = await crud.backend_user.get_multi(db)
    assert test_user not in results
