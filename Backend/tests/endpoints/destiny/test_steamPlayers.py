import pytest
from dummyData.insert import mock_request
from httpx import AsyncClient
from pytest_mock import MockerFixture

from NetworkingSchemas.destiny.steamPlayers import DestinySteamPlayersCountModel


@pytest.mark.asyncio
async def test_get(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/steam_players/get/all")
    assert r.status_code == 200
    data = DestinySteamPlayersCountModel.parse_obj(r.json())
    assert data.entries == []
