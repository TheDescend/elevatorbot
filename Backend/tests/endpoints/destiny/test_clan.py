import pytest
from dummyData.insert import mock_request
from dummyData.static import *
from httpx import AsyncClient
from pytest_mock import MockerFixture

from NetworkingSchemas.destiny.clan import DestinyClanLink, DestinyClanModel


@pytest.mark.asyncio
async def test_clan(client: AsyncClient, mocker: MockerFixture):
    """This tests all function in the file, because link_clan() needs to be called first"""

    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    # =====================================================================
    # no link exists yet
    r = await client.get(f"/destiny/clan/{dummy_discord_guild_id}/get")
    assert r.status_code == 409
    assert r.json()["error"] == "NoClanLink"

    # link clan
    r = await client.post(f"/destiny/clan/{dummy_discord_guild_id}/{dummy_discord_id}/link")
    assert r.status_code == 200
    data = DestinyClanLink.parse_obj(r.json())
    assert data.success is True
    assert data.clan_name == "Descend"

    # link clan (without admin)
    r = await client.post(f"/destiny/clan/{dummy_discord_guild_id}/{dummy_discord_id_without_perms}/link")
    assert r.status_code == 409
    assert r.json()["error"] == "ClanNoPermissions"

    # =====================================================================
    # get clan
    r = await client.get(f"/destiny/clan/{dummy_discord_guild_id}/get")
    assert r.status_code == 200
    data = DestinyClanModel.parse_obj(r.json())
    assert data.id == 4107840
    assert data.name == "Descend"

    # =====================================================================
    # unlink clan
    r = await client.delete(f"/destiny/clan/{dummy_discord_guild_id}/{dummy_discord_id}/unlink")
    assert r.status_code == 200
    data = DestinyClanLink.parse_obj(r.json())
    assert data.success is True
    assert data.clan_name == "Descend"
