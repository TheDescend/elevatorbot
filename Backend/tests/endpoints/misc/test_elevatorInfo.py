import pytest
from dummyData.insert import mock_request
from dummyData.static import *
from httpx import AsyncClient
from pytest_mock import MockerFixture

from Shared.functions.helperFunctions import get_now_with_tz
from Shared.NetworkingSchemas import ElevatorGuildsModel


@pytest.mark.asyncio
async def test_elevator(client: AsyncClient, mocker: MockerFixture):
    """This tests all function in the file, because add_discord_server() needs to be called first"""

    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    # =====================================================================
    # no guild exists yet
    r = await client.get("/elevator/discord_servers/get/all")
    assert r.status_code == 200
    data = ElevatorGuildsModel.parse_obj(r.json())
    assert data.guilds == []

    # =====================================================================
    # add
    r = await client.post(f"/elevator/discord_servers/add/{dummy_discord_guild_id}")
    assert r.status_code == 200

    # =====================================================================
    # get
    r = await client.get("/elevator/discord_servers/get/all")
    assert r.status_code == 200
    data = ElevatorGuildsModel.parse_obj(r.json())
    assert data.guilds != []
    assert len(data.guilds) == 1
    assert data.guilds[0].guild_id == dummy_discord_guild_id
    assert data.guilds[0].join_date.day == get_now_with_tz().day

    # =====================================================================
    # delete
    r = await client.delete(f"/elevator/discord_servers/delete/{dummy_discord_guild_id}")
    assert r.status_code == 200

    # =====================================================================
    # no guild exists again
    r = await client.get("/elevator/discord_servers/get/all")
    assert r.status_code == 200
    data = ElevatorGuildsModel.parse_obj(r.json())
    assert data.guilds == []
