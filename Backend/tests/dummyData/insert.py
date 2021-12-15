import datetime
import json as json_lib
import os
import unittest.mock
from unittest import mock

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
    dummy_refresh_token,
    dummy_token,
)

from Backend.crud import discord_users
from Backend.database.models import DiscordUsers
from Backend.main import app
from Backend.misc.helperFunctions import get_now_with_tz
from Backend.networking.schemas import WebResponse
from NetworkingSchemas.misc.auth import BungieTokenInput


async def mock_request(
    self,
    method: str,
    route: str,
    headers: dict = None,
    params: dict = None,
    json: dict = None,
    form_data: dict = None,
    **kwargs,
) -> WebResponse:
    if method == "GET":
        with open(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "data.json"), "r", encoding="utf-8"
        ) as file:
            dummy_data: dict = json_lib.load(file)
        return WebResponse(0, 200, dummy_data[route], True)

    else:
        raise ValueError(f"Method was not GET, but {method}")


# @unittest.mock.patch.object("Backend.crud.destiny.discordUsers.NetworkBase", "_request", mock_request)


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
