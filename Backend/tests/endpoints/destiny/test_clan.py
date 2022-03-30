import pytest
from dummyData.insert import mock_request
from dummyData.static import *
from httpx import AsyncClient
from pytest_mock import MockerFixture

from Shared.networkingSchemas.destiny.clan import DestinyClanLink, DestinyClanMembersModel, DestinyClanModel
from Shared.networkingSchemas.destiny.profile import DestinyProfileModel


@pytest.mark.asyncio
async def test_clan(client: AsyncClient, mocker: MockerFixture):
    """This tests all function in the file, because link_clan() needs to be called first"""

    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)

    # =====================================================================
    # no link exists yet
    r = await client.get(f"/destiny/clan/{dummy_discord_guild_id}/get")
    assert r.status_code == 409
    assert r.json()["error"] == "NoClanLink"

    # link clan
    r = await client.post(f"/destiny/clan/{dummy_discord_guild_id}/{dummy_discord_id}/link")
    assert r.status_code == 200
    data = DestinyClanLink.parse_obj(r.json())
    assert bool(data) is True
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
    # get clan members
    r = await client.get(f"/destiny/clan/{dummy_discord_guild_id}/members")
    assert r.status_code == 200
    data = DestinyClanMembersModel.parse_obj(r.json())
    assert data.members
    assert len(data.members) == 1
    assert data.members[0].system == dummy_destiny_system
    assert data.members[0].destiny_id == dummy_destiny_id
    assert data.members[0].name == "Tom#1234"
    assert data.members[0].is_online is True
    assert data.members[0].last_online_status_change.day == 5
    assert data.members[0].join_date.day == 6
    assert data.members[0].discord_id == dummy_discord_id

    r = await client.get(f"/destiny/clan/{dummy_discord_guild_id}/members/no_cache")
    assert r.status_code == 200
    data = DestinyClanMembersModel.parse_obj(r.json())
    assert len(data.members) == 1
    assert data.members[0].destiny_id == dummy_destiny_id

    r = await client.get(f"/destiny/clan/{dummy_discord_guild_id}/members/search/tom")
    assert r.status_code == 200
    data = DestinyClanMembersModel.parse_obj(r.json())
    assert len(data.members) == 1
    assert data.members[0].destiny_id == dummy_destiny_id

    # =====================================================================
    # invite to clan
    r = await client.post(f"/destiny/clan/{dummy_discord_guild_id}/invite/{dummy_discord_id}")
    assert r.status_code == 200
    data = DestinyProfileModel.parse_obj(r.json())
    assert data.discord_id == dummy_discord_id

    # =====================================================================
    # kick from clan
    r = await client.post(f"/destiny/clan/{dummy_discord_guild_id}/kick/{dummy_discord_id}")
    assert r.status_code == 200
    data = DestinyProfileModel.parse_obj(r.json())
    assert data.discord_id == dummy_discord_id

    # =====================================================================
    # unlink clan
    r = await client.delete(f"/destiny/clan/{dummy_discord_guild_id}/{dummy_discord_id}/unlink")
    assert r.status_code == 200
    data = DestinyClanLink.parse_obj(r.json())
    assert bool(data) is True
    assert data.clan_name == "Descend"
