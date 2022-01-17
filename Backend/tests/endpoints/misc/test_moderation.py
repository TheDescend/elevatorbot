import pytest
from dummyData.insert import mock_request
from dummyData.static import *
from httpx import AsyncClient
from orjson import orjson
from pytest_mock import MockerFixture

from Shared.functions.helperFunctions import get_now_with_tz
from Shared.networkingSchemas.misc.moderation import ModerationAddModel, ModerationModel, ModerationsModel


@pytest.mark.asyncio
async def test_mute(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    # =====================================================================
    # no mute exists yet
    r = await client.get(f"/moderation/{dummy_discord_guild_id}/{dummy_discord_id}/mute")
    assert r.status_code == 200
    data = ModerationsModel.parse_obj(r.json())
    assert data.entries == []

    # =====================================================================
    # add mute
    input_model = ModerationAddModel(
        mod_discord_id=dummy_discord_id_without_perms, reason="I felt like it", duration_in_seconds=100
    )
    r = await client.post(
        f"/moderation/{dummy_discord_guild_id}/{dummy_discord_id}/mute", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = ModerationModel.parse_obj(r.json())
    assert data.type == "mute"
    assert data.duration_in_seconds == 100
    assert_moderation(data)

    # =====================================================================
    # get mute
    r = await client.get(f"/moderation/{dummy_discord_guild_id}/{dummy_discord_id}/mute")
    assert r.status_code == 200
    data = ModerationsModel.parse_obj(r.json())
    assert data.entries != []
    assert len(data.entries) == 1
    assert data.entries[0].type == "mute"
    assert data.entries[0].duration_in_seconds == 100
    assert_moderation(data.entries[0])


@pytest.mark.asyncio
async def test_warning(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    # =====================================================================
    # no warning exists yet
    r = await client.get(f"/moderation/{dummy_discord_guild_id}/{dummy_discord_id}/warning")
    assert r.status_code == 200
    data = ModerationsModel.parse_obj(r.json())
    assert data.entries == []

    # =====================================================================
    # add warning
    input_model = ModerationAddModel(mod_discord_id=dummy_discord_id_without_perms, reason="I felt like it")
    r = await client.post(
        f"/moderation/{dummy_discord_guild_id}/{dummy_discord_id}/warning", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = ModerationModel.parse_obj(r.json())
    assert data.type == "warning"
    assert data.duration_in_seconds is None
    assert_moderation(data)

    # =====================================================================
    # get warning
    r = await client.get(f"/moderation/{dummy_discord_guild_id}/{dummy_discord_id}/warning")
    assert r.status_code == 200
    data = ModerationsModel.parse_obj(r.json())
    assert data.entries != []
    assert len(data.entries) == 1
    assert data.entries[0].type == "warning"
    assert data.entries[0].duration_in_seconds is None
    assert_moderation(data.entries[0])


def assert_moderation(data: ModerationModel):
    """Tests that the moderation is OK"""

    assert data.guild_id == dummy_discord_guild_id
    assert data.discord_id == dummy_discord_id
    assert data.mod_discord_id == dummy_discord_id_without_perms
    assert data.reason == "I felt like it"
    assert data.date.day == get_now_with_tz().day
