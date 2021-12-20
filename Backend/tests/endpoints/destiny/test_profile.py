import pytest
from dummyData.insert import mock_request
from dummyData.static import *
from httpx import AsyncClient
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from NetworkingSchemas.destiny.profile import DestinyHasTokenModel, DestinyProfileModel


@pytest.mark.asyncio
async def test_discord_get(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/profile/discord/{dummy_discord_id}")
    assert r.status_code == 200
    data = DestinyProfileModel.parse_obj(r.json())
    assert data.discord_id == dummy_discord_id
    assert data.destiny_id == dummy_destiny_id
    assert data.system == dummy_destiny_system
    assert data.bungie_name == dummy_bungie_name


@pytest.mark.asyncio
async def test_discord_has_token(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/profile/{dummy_discord_id}/has_token")
    assert r.status_code == 200
    data = DestinyHasTokenModel.parse_obj(r.json())
    assert data.token is True
    assert data.value == str(dummy_token)


@pytest.mark.asyncio
async def test_discord_registration_role(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    # this does not fail, but does not do anything either, since no registration roles exist
    r = await client.get(f"/destiny/profile/{dummy_discord_guild_id}/{dummy_discord_id}/registration_role")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_destiny_get(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/profile/destiny/{dummy_destiny_id}")
    assert r.status_code == 200
    data = DestinyProfileModel.parse_obj(r.json())
    assert data.discord_id == dummy_discord_id
    assert data.destiny_id == dummy_destiny_id
    assert data.system == dummy_destiny_system
    assert data.bungie_name == dummy_bungie_name


@pytest.mark.asyncio
async def test_discord_delete(client: AsyncClient, mocker: MockerFixture, db: AsyncSession):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.delete(f"/destiny/profile/98/delete")
    assert r.status_code == 409
    assert r.json()["error"] == "DiscordIdNotFound"

    r = await client.delete(f"/destiny/profile/99/delete")
    assert r.status_code == 200
