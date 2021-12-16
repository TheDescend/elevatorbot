import datetime
import json as json_lib
import os
import unittest.mock
from unittest import mock
from urllib.parse import urlencode

from httpx import AsyncClient
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession
from static import (
    dummy_bungie_name,
    dummy_destiny_id,
    dummy_destiny_system,
    dummy_discord_channel_id,
    dummy_discord_guild_id,
    dummy_discord_id,
    dummy_instance_id,
    dummy_refresh_token,
    dummy_token,
)

from Backend.core.destiny.activities import DestinyActivities
from Backend.crud import crud_activities, crud_activities_fail_to_get, discord_users
from Backend.database.models import DiscordUsers
from Backend.main import app
from Backend.misc.cache import cache
from Backend.misc.helperFunctions import get_now_with_tz
from Backend.networking.schemas import WebResponse
from NetworkingSchemas.misc.auth import BungieTokenInput


async def mock_request(
    self,
    method: str,
    route: str,
    headers: dict = None,
    params=None,
    json: dict = None,
    form_data: dict = None,
    **kwargs,
) -> WebResponse:
    if params is None:
        params = {}

    if method == "GET":
        with open(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "data.json"), "r", encoding="utf-8"
        ) as file:
            dummy_data: dict = json_lib.load(file)

        # capture the required route when this fails
        param_route = f"{route}?{urlencode(params)}"
        try:
            return WebResponse(0, 200, dummy_data[param_route], True)
        except KeyError as e:
            print("Tried to call this route, but it doesnt exist in the dummy data:")
            print(route)
            raise e

    else:
        raise ValueError(f"Method was not GET, but {method}")


@unittest.mock.patch("Backend.networking.base.NetworkBase._request", mock_request)
async def insert_dummy_data(db: AsyncSession):
    # create our registered destiny user
    token_data = BungieTokenInput(
        access_token=dummy_token,
        token_type="EMPTY",
        expires_in=999999999,
        refresh_token=dummy_refresh_token,
        refresh_expires_in=999999999,
        membership_id=dummy_destiny_id,
        state=f"{dummy_discord_id}:{dummy_discord_guild_id}:{dummy_discord_channel_id}",
    )

    # insert the user
    result, user, discord_id, guild_id = await discord_users.insert_profile(db=db, bungie_token=token_data)

    assert result.success is True
    assert user.destiny_id == dummy_destiny_id
    assert discord_id == dummy_discord_id
    assert guild_id == dummy_discord_guild_id

    # update their activities
    activities = DestinyActivities(db=db, user=user)
    await activities.update_activity_db()

    assert activities._full_character_list == [{"char_id": 666, "deleted": False}]
    assert user.activities_last_updated.day == 15
    assert user.activities_last_updated.month == 12
    assert dummy_instance_id in cache.saved_pgcrs

    fail = await crud_activities_fail_to_get.get_all(db=db)
    assert not fail

    pgcr = await crud_activities.get(db=db, instance_id=dummy_instance_id)
    assert pgcr is not None

    # try that again, it should not throw any error (which means it did not try to insert again)
    await activities.update_activity_db()
