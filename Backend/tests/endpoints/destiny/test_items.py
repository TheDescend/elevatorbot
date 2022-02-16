import pytest
from dummyData.insert import mock_request
from dummyData.static import *
from httpx import AsyncClient
from pytest_mock import MockerFixture

from Shared.networkingSchemas import DestinyAllCollectibleModel, DestinyAllTriumphModel, NameModel
from Shared.networkingSchemas.destiny import DestinyAllLoreModel


@pytest.mark.asyncio
async def test_get_collectible_name(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/items/collectible/{dummy_gotten_collectible_id}")
    assert r.status_code == 200
    data = NameModel.parse_obj(r.json())
    assert data.name == "Earned Collectible"


@pytest.mark.asyncio
async def test_get_all_collectible(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get("/destiny/items/collectible/get/all")
    assert r.status_code == 200
    data = DestinyAllCollectibleModel.parse_obj(r.json())
    assert data.collectibles
    assert len(data.collectibles) > 0


@pytest.mark.asyncio
async def test_get_triumph_name(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/items/triumph/{dummy_gotten_record_id}")
    assert r.status_code == 200
    data = NameModel.parse_obj(r.json())
    assert data.name == "Gotten Record"


@pytest.mark.asyncio
async def test_get_all_triumphs(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get("/destiny/items/triumph/get/all")
    assert r.status_code == 200
    data = DestinyAllTriumphModel.parse_obj(r.json())
    assert data.triumphs
    assert len(data.triumphs) > 0


@pytest.mark.asyncio
async def test_get_all_lore(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get("/destiny/items/lore/get/all")
    assert r.status_code == 200
    data = DestinyAllLoreModel.parse_obj(r.json())
    assert data.items
    assert len(data.items) == 1
    assert data.items[0].reference_id == dummy_lore_id
    assert data.items[0].name == "The Gate Lord's Eye"
    assert (
        data.items[0].description
        == "An iris unfurls. Our gaze caught. Cortex clutched. Suspended.\n\nA million lights bend inward. Pulled on a wave of enigmatic tone.\n\nA million "
        "lights rip inward. Fall. Link. Scream. Cycle. Bleed. Blend. Cycle.\n\nOne light alone. Pulled. Discordant. Suspended in the "
        "Endless.\n\nScreams.\n\nAn iris unfurls.\n\nRun. Run. Run.\n\nAn iris unfurls.\n\nRun. Run.\n\nAn iris unfurls.\n\nRun.\n\nBlink. An iris folds in."
    )
    assert data.items[0].sub_title == "It looks through you, toward the infinite."
    assert data.items[0].redacted is False
