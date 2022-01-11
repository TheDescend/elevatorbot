import datetime

import pytest
from dummyData.insert import mock_request
from dummyData.static import *
from httpx import AsyncClient
from orjson import orjson
from pytest_mock import MockerFixture

from Shared.functions.helperFunctions import get_now_with_tz
from Shared.NetworkingSchemas.destiny.lfgSystem import (
    AllLfgDeleteOutputModel,
    AllLfgOutputModel,
    LfgCreateInputModel,
    LfgOutputModel,
    LfgUpdateInputModel,
    UserAllLfgOutputModel,
)


@pytest.mark.asyncio
async def test_lfg(client: AsyncClient, mocker: MockerFixture):
    """This tests all function in the file, because create() needs to be called first"""

    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    # =====================================================================
    # no lfg exists yet
    r = await client.get(f"/destiny/lfg/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = AllLfgOutputModel.parse_obj(r.json())
    assert data.events == []

    # =====================================================================
    # create
    input_model = LfgCreateInputModel(
        activity="Standing Around",
        description="Test LFG Event",
        start_time=datetime.datetime(day=10, month=10, year=2030, tzinfo=datetime.timezone.utc),
        max_joined_members=6,
        joined_members=[1, 2, dummy_discord_id],
        backup_members=[4],
    )
    r = await client.post(
        f"/destiny/lfg/{dummy_discord_guild_id}/{dummy_discord_id}/create", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = LfgOutputModel.parse_obj(r.json())
    assert_lfg_event_ok(data=data)
    assert data.message_id is None
    assert data.voice_channel_id is None

    # =====================================================================
    # update
    input_model = LfgUpdateInputModel(message_id=1, voice_channel_id=2)
    r = await client.post(
        f"/destiny/lfg/{dummy_discord_guild_id}/{dummy_discord_id}/update/1", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = LfgOutputModel.parse_obj(r.json())
    assert_lfg_event_ok(data=data)
    assert data.message_id == 1
    assert data.voice_channel_id == 2

    # =====================================================================
    # get all
    r = await client.get(f"/destiny/lfg/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = AllLfgOutputModel.parse_obj(r.json())
    assert len(data.events) == 1
    assert_lfg_event_ok(data=data.events[0])

    # =====================================================================
    # get
    r = await client.get(f"/destiny/lfg/{dummy_discord_guild_id}/get/1")
    assert r.status_code == 200
    data = LfgOutputModel.parse_obj(r.json())
    assert_lfg_event_ok(data=data)

    # =====================================================================
    # user get all
    r = await client.get(f"/destiny/lfg/{dummy_discord_guild_id}/{dummy_discord_id}/get/all")
    assert r.status_code == 200
    data = UserAllLfgOutputModel.parse_obj(r.json())
    assert len(data.joined) == 1
    assert len(data.backup) == 0
    assert_lfg_event_ok(data=data.joined[0])

    # =====================================================================
    # delete
    # this needs to re-add the event a couple of times
    r = await client.delete(f"/destiny/lfg/{dummy_discord_guild_id}/{dummy_discord_id_without_perms}/delete/1")
    assert r.status_code == 409
    assert r.json()["error"] == "NoLfgEventPermissions"

    r = await client.delete(f"/destiny/lfg/{dummy_discord_guild_id}/{dummy_discord_id}/delete/1")
    assert r.status_code == 200

    input_model = LfgCreateInputModel(
        activity="Standing Around",
        description="Test LFG Event",
        start_time=datetime.datetime(day=10, month=10, year=2030, tzinfo=datetime.timezone.utc),
        max_joined_members=6,
        joined_members=[1, 2, dummy_discord_id],
        backup_members=[4],
    )
    r = await client.post(
        f"/destiny/lfg/{dummy_discord_guild_id}/{dummy_discord_id}/create", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = LfgOutputModel.parse_obj(r.json())
    assert data.id == 2

    r = await client.delete(f"/destiny/lfg/{dummy_discord_guild_id}/1/delete/2")
    assert r.status_code == 200

    # =====================================================================
    # delete all
    r = await client.post(
        f"/destiny/lfg/{dummy_discord_guild_id}/{dummy_discord_id}/create", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = LfgOutputModel.parse_obj(r.json())
    assert data.id == 3

    r = await client.delete(f"/destiny/lfg/{dummy_discord_guild_id}/delete/all")
    assert r.status_code == 200
    data = AllLfgDeleteOutputModel.parse_obj(r.json())
    assert data.event_ids == [3]


def assert_lfg_event_ok(data: LfgOutputModel):
    """Tests all attrs of the obj"""

    assert data.id == 1
    assert data.guild_id == dummy_discord_guild_id
    assert data.channel_id == dummy_persistent_lfg_channel_id
    assert data.author_id == dummy_discord_id
    assert data.activity == "Standing Around"
    assert data.description == "Test LFG Event"
    assert data.start_time == datetime.datetime(day=10, month=10, year=2030, tzinfo=datetime.timezone.utc)
    assert data.max_joined_members == 6
    assert data.joined_members == [1, 2, dummy_discord_id]
    assert data.backup_members == [4]
    assert data.creation_time.day == get_now_with_tz().day
    assert data.voice_category_channel_id == dummy_persistent_lfg_voice_category_id
