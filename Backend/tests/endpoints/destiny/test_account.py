import datetime

import pytest as pytest
from dummyData.insert import mock_bungio_request, mock_request
from dummyData.static import *
from httpx import AsyncClient
from orjson import orjson
from pytest_mock import MockerFixture

from Backend.bungio.manifest import destiny_manifest
from Backend.misc.cache import cache
from Shared.networkingSchemas import BoolModel, DestinyAllMaterialsModel, NameModel, ValueModel
from Shared.networkingSchemas.destiny import (
    BoolModelRecord,
    DestinyCatalystsModel,
    DestinyCharactersModel,
    DestinyLowMansByCategoryModel,
    DestinySealsModel,
    DestinyStatInputModel,
    DestinyTimeInputModel,
    DestinyTimesModel,
    DestinyTriumphScoreModel,
    SeasonalChallengesModel,
)
from Shared.networkingSchemas.destiny.account import DestinyCraftableModel


@pytest.mark.asyncio
async def test_destiny_name(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/name/")
    assert r.status_code == 200
    data = NameModel.parse_obj(r.json())
    assert data.name == dummy_bungie_name

    r = await client.get("/destiny/account/0/0/name")
    assert r.status_code == 409
    assert r.json() == {"error": "DiscordIdNotFound"}


@pytest.mark.asyncio
async def test_has_collectible(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(
        f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/collectible/{dummy_gotten_collectible_id}"
    )
    assert r.status_code == 200
    data = BoolModel.parse_obj(r.json())
    assert data.bool is True
    assert dummy_gotten_collectible_id in cache.collectibles[dummy_destiny_id]

    # run the same test again to see that the cache works
    r = await client.get(
        f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/collectible/{dummy_gotten_collectible_id}"
    )
    assert r.status_code == 200

    r = await client.get(
        f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/collectible/{dummy_not_gotten_collectible_id}"
    )
    assert r.status_code == 200
    data = BoolModel.parse_obj(r.json())
    assert data.bool is False
    assert dummy_not_gotten_collectible_id not in cache.collectibles[dummy_destiny_id]


@pytest.mark.asyncio
async def test_has_triumph(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(
        f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/triumph/{dummy_gotten_record_id}"
    )
    assert r.status_code == 200
    data = BoolModelRecord.parse_obj(r.json())
    assert data.bool is True
    assert data.objectives == []
    assert dummy_gotten_record_id in cache.triumphs[dummy_destiny_id]

    # run the same test again to see that the cache works
    r = await client.get(
        f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/triumph/{dummy_gotten_record_id}"
    )
    assert r.status_code == 200

    r = await client.get(
        f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/triumph/{dummy_not_gotten_record_id}"
    )
    assert r.status_code == 200
    data = BoolModelRecord.parse_obj(r.json())
    assert data.bool is False
    assert data.objectives[0].bool is True
    assert data.objectives[1].bool is False
    assert dummy_not_gotten_record_id not in cache.triumphs[dummy_destiny_id]


@pytest.mark.asyncio
async def test_metric(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/metric/{dummy_metric_id}")
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == dummy_metric_value


@pytest.mark.asyncio
async def test_destiny_solos(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/solos")
    assert r.status_code == 200
    data = DestinyLowMansByCategoryModel.parse_obj(r.json())
    assert data.categories
    assert data.categories[0].category == "Dungeons"
    assert data.categories[0].solos
    assert data.categories[0].solos[0].activity_name == dummy_activity_name
    assert data.categories[0].solos[0].activity_ids == [1337]
    assert data.categories[0].solos[0].count == 1
    assert data.categories[0].solos[0].flawless_count == 0
    assert data.categories[0].solos[0].not_flawless_count == 1
    assert data.categories[0].solos[0].fastest.seconds == 557


@pytest.mark.asyncio
async def test_characters(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/characters")
    assert r.status_code == 200
    data = DestinyCharactersModel.parse_obj(r.json())
    assert data.characters
    assert data.characters[0].character_id == dummy_character_id


@pytest.mark.asyncio
async def test_stat(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    input_model = DestinyStatInputModel(stat_name="kills", stat_category="allPvE")
    r = await client.post(f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/stat", json=input_model.dict())
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 1041425

    input_model = DestinyStatInputModel(stat_name="kills", stat_category="allTime")
    r = await client.post(f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/stat", json=input_model.dict())
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 1088957


@pytest.mark.asyncio
async def test_stat_characters(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    input_model = DestinyStatInputModel(stat_name="kills", stat_category="allPvE")
    r = await client.post(
        f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/stat/character/{dummy_character_id}",
        json=input_model.dict(),
    )
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 525128

    input_model = DestinyStatInputModel(stat_name="kills", stat_category="allTime")
    r = await client.post(
        f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/stat/character/{dummy_character_id}",
        json=input_model.dict(),
    )
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 540326

    input_model = DestinyStatInputModel(stat_name="kills", stat_category="allTime")
    r = await client.post(
        f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/stat/character/1", json=input_model.dict()
    )
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_time(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    input_model = DestinyTimeInputModel(
        start_time=datetime.datetime(year=2021, month=12, day=1, tzinfo=datetime.timezone.utc),
        end_time=datetime.datetime(year=2021, month=12, day=31, tzinfo=datetime.timezone.utc),
        modes=[4],
        activity_ids=None,
        character_class=None,
    )
    r = await client.post(
        f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/time", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTimesModel.parse_obj(r.json())
    assert data.entries
    assert len(data.entries) == 1
    assert data.entries[0].time_played == 557 + 9
    assert data.entries[0].mode == 4
    assert data.entries[0].activity_ids is None

    input_model = DestinyTimeInputModel(
        start_time=datetime.datetime(year=2021, month=12, day=30, tzinfo=datetime.timezone.utc),
        end_time=datetime.datetime(year=2021, month=12, day=31, tzinfo=datetime.timezone.utc),
        modes=[4],
        activity_ids=None,
        character_class=None,
    )
    r = await client.post(
        f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/time", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTimesModel.parse_obj(r.json())
    assert data.entries
    assert data.entries[0].time_played == 0

    input_model = DestinyTimeInputModel(
        start_time=datetime.datetime(year=2021, month=12, day=1, tzinfo=datetime.timezone.utc),
        end_time=datetime.datetime(year=2021, month=12, day=31, tzinfo=datetime.timezone.utc),
        modes=[4],
        activity_ids=None,
        character_class="Hunter",
    )
    r = await client.post(
        f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/time", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTimesModel.parse_obj(r.json())
    assert data.entries
    assert data.entries[0].time_played != 0

    input_model = DestinyTimeInputModel(
        start_time=datetime.datetime(year=2021, month=12, day=1, tzinfo=datetime.timezone.utc),
        end_time=datetime.datetime(year=2021, month=12, day=31, tzinfo=datetime.timezone.utc),
        modes=[4],
        activity_ids=None,
        character_class="Warlock",
    )
    r = await client.post(
        f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/time", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTimesModel.parse_obj(r.json())
    assert data.entries
    assert data.entries[0].time_played == 0

    input_model = DestinyTimeInputModel(
        start_time=datetime.datetime(year=2021, month=12, day=1, tzinfo=datetime.timezone.utc),
        end_time=datetime.datetime(year=2021, month=12, day=31, tzinfo=datetime.timezone.utc),
        modes=[4],
        activity_ids=[768123],
        character_class=None,
    )
    r = await client.post(
        f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/time", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTimesModel.parse_obj(r.json())
    assert data.entries
    assert data.entries[1].time_played == 0

    input_model = DestinyTimeInputModel(
        start_time=datetime.datetime(year=2021, month=12, day=1, tzinfo=datetime.timezone.utc),
        end_time=datetime.datetime(year=2021, month=12, day=31, tzinfo=datetime.timezone.utc),
        modes=[14896844],
        activity_ids=[dummy_activity_reference_id],
        character_class=None,
    )
    r = await client.post(
        f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/time", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTimesModel.parse_obj(r.json())
    assert data.entries
    assert data.entries[1].time_played != 0


@pytest.mark.asyncio
async def test_seasonal_challenges(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/seasonal_challenges")
    assert r.status_code == 200
    data = SeasonalChallengesModel.parse_obj(r.json())
    assert data.topics
    assert data.topics[0].name == "Seasonal"
    assert data.topics[0].seasonal_challenges[0].completion_percentage == 1.0
    assert data.topics[0].seasonal_challenges[0].name == "Master of All"

    assert destiny_manifest._manifest_seasonal_challenges_definition is not None


@pytest.mark.asyncio
async def test_triumphs(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/triumphs")
    assert r.status_code == 200
    data = DestinyTriumphScoreModel.parse_obj(r.json())
    assert data.active_score == 20097
    assert data.legacy_score == 117570
    assert data.lifetime_score == 137667


@pytest.mark.asyncio
async def test_artifact_level(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/artifact")
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 20


@pytest.mark.asyncio
async def test_season_pass_level(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/season_pass")
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 210


@pytest.mark.asyncio
async def test_get_material_amount(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/materials")
    assert r.status_code == 200
    data = DestinyAllMaterialsModel.parse_obj(r.json())
    assert data.basic
    assert data.transmog
    assert data.upgrading
    assert data.crafting
    assert data.special


@pytest.mark.asyncio
async def test_get_consumable_amount(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(
        f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/consumable/{dummy_consumable_id}"
    )
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 17


@pytest.mark.asyncio
async def test_get_max_power(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/max_power")
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 1000


@pytest.mark.asyncio
async def test_get_vault_space(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/vault_space")
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 9


@pytest.mark.asyncio
async def test_get_bright_dust(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/bright_dust")
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 50


@pytest.mark.asyncio
async def test_get_legendary_shards(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/shards")
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 100


@pytest.mark.asyncio
async def test_get_catalyst_completion(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/catalysts")
    assert r.status_code == 200
    data = DestinyCatalystsModel.parse_obj(r.json())
    assert data.completed == 1
    assert len(data.power) == 2
    assert data.power[0].name == "Tractor Cannon Catalyst"
    assert data.power[0].complete is True
    assert data.power[0].completion_percentage == 1
    assert data.power[0].completion_status == "FF"
    assert data.power[1].name == "Acrius Catalyst"
    assert data.power[1].complete is False
    assert data.power[1].completion_percentage == 0.75
    assert data.power[1].completion_status == "FD"


@pytest.mark.asyncio
async def test_get_seal_completion(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/seals")
    assert r.status_code == 200
    data = DestinySealsModel.parse_obj(r.json())
    assert len(data.completed) == 2
    assert data.completed[0].name == "Gambit"
    assert data.completed[1].name == "Not Gambit"
    assert len(data.not_completed) == 1
    assert data.not_completed[0].name == "Destinations"
    assert len(data.guilded) == 1
    assert data.guilded[0].name == "Gambit"
    assert len(data.not_guilded) == 1
    assert data.not_guilded[0].name == "Not Gambit"

    assert destiny_manifest._manifest_seals != {}


@pytest.mark.asyncio
async def test_get_craftables(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    r = await client.get(f"/destiny/account/{dummy_discord_guild_id}/{dummy_discord_id}/craftables")
    assert r.status_code == 200
    data = [DestinyCraftableModel.parse_obj(res) for res in r.json()]
    assert len(data) == 1
