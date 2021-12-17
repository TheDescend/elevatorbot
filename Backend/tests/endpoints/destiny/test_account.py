import pytest as pytest
from dummyData.insert import mock_request
from httpx import AsyncClient
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession
from static import (
    dummy_activity_name,
    dummy_bungie_name,
    dummy_destiny_id,
    dummy_discord_guild_id,
    dummy_discord_id,
    dummy_gotten_collectible_id,
    dummy_gotten_record_id,
    dummy_metric_id,
    dummy_metric_value,
    dummy_not_gotten_collectible_id,
    dummy_not_gotten_record_id,
)

from Backend.misc.cache import cache
from NetworkingSchemas.basic import BoolModel, NameModel, ValueModel
from NetworkingSchemas.destiny.account import BoolModelRecord, DestinyLowMansModel


@pytest.mark.asyncio
async def test_destiny_name(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/name/")
    assert r.status_code == 200
    data = NameModel.parse_obj(r.json())
    assert data.name == dummy_bungie_name

    r = await client.get(f"/destiny/0/0/account/name")
    assert r.status_code == 409
    assert r.json() == {"error": "DiscordIdNotFound"}


@pytest.mark.asyncio
async def test_has_collectible(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/collectible/{dummy_gotten_collectible_id}"
    )
    assert r.status_code == 200
    data = BoolModel.parse_obj(r.json())
    assert data.bool is True
    assert dummy_gotten_collectible_id in cache.collectibles[dummy_destiny_id]

    r = await client.get(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/collectible/{dummy_not_gotten_collectible_id}"
    )
    assert r.status_code == 200
    data = BoolModel.parse_obj(r.json())
    assert data.bool is False
    assert dummy_not_gotten_collectible_id not in cache.collectibles[dummy_destiny_id]


@pytest.mark.asyncio
async def test_has_triumph(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/triumph/{dummy_gotten_record_id}"
    )
    assert r.status_code == 200
    data = BoolModelRecord.parse_obj(r.json())
    assert data.bool is True
    assert data.objectives == []
    assert dummy_gotten_record_id in cache.triumphs[dummy_destiny_id]

    r = await client.get(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/triumph/{dummy_not_gotten_record_id}"
    )
    assert r.status_code == 200
    data = BoolModelRecord.parse_obj(r.json())
    assert data.bool is False
    assert data.objectives[0].bool is True
    assert data.objectives[1].bool is False
    assert dummy_not_gotten_record_id not in cache.triumphs[dummy_destiny_id]


@pytest.mark.asyncio
async def test_metric(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/metric/{dummy_metric_id}")
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == dummy_metric_value


@pytest.mark.asyncio
async def test_destiny_solos(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/solos")
    assert r.status_code == 200
    data = DestinyLowMansModel.parse_obj(r.json())
    assert data.solos
    assert data.solos[0].activity_name == dummy_activity_name
    assert data.solos[0].activity_ids == [1337]
    assert data.solos[0].count == 1
    assert data.solos[0].flawless_count == 0
    assert data.solos[0].not_flawless_count == 1
    assert data.solos[0].fastest.seconds == 557
