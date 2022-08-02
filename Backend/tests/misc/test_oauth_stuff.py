import datetime

import pytest
from bungio.error import InvalidAuthentication
from bungio.models import AuthData
from dummyData.insert import mock_bungio_request, mock_request
from dummyData.static import dummy_destiny_id, dummy_destiny_system
from httpx import AsyncClient
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.bungio.client import get_bungio_client
from Backend.crud import discord_users
from Shared.functions.helperFunctions import get_min_with_tz, get_now_with_tz


@pytest.mark.asyncio
async def test_check_oauth(client: AsyncClient, mocker: MockerFixture, db: AsyncSession):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    valid = AuthData(
        bungie_name="valid#1234",
        token="token",
        token_expiry=get_min_with_tz(),
        refresh_token="refresh",
        refresh_token_expiry=get_now_with_tz() + datetime.timedelta(days=1000),
        membership_id=9999999,
        membership_type=dummy_destiny_system,
    )
    result, user, discord_id, guild_id = await discord_users.insert_profile(
        db=db, auth=valid, state=f"9999999:9999999:9999999"
    )

    # refresh the token
    await user.auth.refresh()

    # create a user with invalid auth data and try to refresh that to check the invalidation
    invalid = AuthData(
        bungie_name="invalid#1234",
        token="abc",
        token_expiry=get_min_with_tz(),
        refresh_token="def",
        refresh_token_expiry=get_min_with_tz(),
        membership_id=1686521,
        membership_type=dummy_destiny_system,
    )
    try:
        await get_bungio_client().api.get_bungie_applications(auth=invalid)
    except InvalidAuthentication:
        pass
    else:
        raise AssertionError
    assert invalid.token is None
