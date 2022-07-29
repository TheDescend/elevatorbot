import pytest
from dummyData.insert import mock_bungio_request, mock_request
from dummyData.static import *
from httpx import AsyncClient
from pytest_mock import MockerFixture

from Shared.networkingSchemas.misc.giveaway import GiveawayModel


@pytest.mark.asyncio
async def test_giveaway(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    # =====================================================================
    # no giveaway exists yet
    r = await client.get(f"/giveaway/{dummy_discord_guild_id}/{dummy_discord_id}/1/get")
    assert r.status_code == 409
    assert r.json()["error"] == "NoGiveaway"

    r = await client.post(f"/giveaway/{dummy_discord_guild_id}/{dummy_discord_id}/1/insert")
    assert r.status_code == 409
    assert r.json()["error"] == "NoGiveaway"

    # create giveaway
    r = await client.post(f"/giveaway/{dummy_discord_guild_id}/{dummy_discord_id}/1/create")
    assert r.status_code == 200

    # get giveaway
    r = await client.get(f"/giveaway/{dummy_discord_guild_id}/{dummy_discord_id}/1/get")
    assert r.status_code == 200
    data = GiveawayModel.parse_obj(r.json())
    assert data.message_id == 1
    assert data.author_id == dummy_discord_id
    assert data.guild_id == dummy_discord_guild_id
    assert data.discord_ids == []

    # insert into giveaway
    r = await client.post(f"/giveaway/{dummy_discord_guild_id}/{dummy_discord_id}/1/insert")
    assert r.status_code == 200
    data = GiveawayModel.parse_obj(r.json())
    assert data.message_id == 1
    assert data.author_id == dummy_discord_id
    assert data.guild_id == dummy_discord_guild_id
    assert data.discord_ids == [dummy_discord_id]

    # insert into giveaway
    r = await client.post(f"/giveaway/{dummy_discord_guild_id}/{dummy_discord_id}/1/insert")
    assert r.status_code == 409
    assert r.json()["error"] == "AlreadyInGiveaway"

    # remove from giveaway
    r = await client.post(f"/giveaway/{dummy_discord_guild_id}/{dummy_discord_id}/1/remove")
    assert r.status_code == 200
    data = GiveawayModel.parse_obj(r.json())
    assert data.message_id == 1
    assert data.author_id == dummy_discord_id
    assert data.guild_id == dummy_discord_guild_id
    assert data.discord_ids == []

    r = await client.post(f"/giveaway/{dummy_discord_guild_id}/{dummy_discord_id}/1/remove")
    assert r.status_code == 200
    data = GiveawayModel.parse_obj(r.json())
    assert data.message_id == 1
    assert data.author_id == dummy_discord_id
    assert data.guild_id == dummy_discord_guild_id
    assert data.discord_ids == []
