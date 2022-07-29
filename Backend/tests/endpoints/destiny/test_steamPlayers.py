import pytest
from dummyData.insert import mock_bungio_request, mock_request
from httpx import AsyncClient
from pytest_mock import MockerFixture

from Shared.networkingSchemas.destiny import DestinySteamPlayersCountModel


@pytest.mark.asyncio
async def test_get(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get("/destiny/steam_players/get/all")
    assert r.status_code == 200
    data = DestinySteamPlayersCountModel.parse_obj(r.json())
    assert data.entries == []
