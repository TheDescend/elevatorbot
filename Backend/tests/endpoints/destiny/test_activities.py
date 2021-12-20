import pytest
from dummyData.insert import mock_request
from dummyData.static import *
from httpx import AsyncClient
from orjson import orjson
from pytest_mock import MockerFixture

from NetworkingSchemas.destiny.activities import (
    DestinyActivitiesModel,
    DestinyActivityDetailsModel,
    DestinyActivityInputModel,
    DestinyActivityOutputModel,
    DestinyLastInputModel,
)


@pytest.mark.asyncio
async def test_get_all(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/activities/get/all")
    assert r.status_code == 200
    data = DestinyActivitiesModel.parse_obj(r.json())
    assert data.activities
    assert len(data.activities) > 0
    assert data.activities[0].name == "Prophecy"
    assert (
        data.activities[0].description
        == 'Enter the realm of the Nine and ask the question: "What is the nature of the Darkness?"'
    )
    assert data.activities[0].activity_ids == [1337]
    assert data.activities[0].mode == 4


@pytest.mark.asyncio
async def test_last(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    input_model = DestinyLastInputModel(completed=True)
    r = await client.post(
        f"/destiny/activities/{dummy_discord_guild_id}/{dummy_discord_id}/last", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyActivityDetailsModel.parse_obj(r.json())
    assert data.instance_id == dummy_instance_id
    assert data.reference_id == dummy_activity_reference_id
    assert data.period.day == 15
    assert data.starting_phase_index == 0
    assert data.activity_duration_seconds == 917
    assert data.score == 17
    assert data.users
    assert len(data.users) == 1
    assert data.users[0].bungie_name == dummy_bungie_name
    assert data.users[0].destiny_id == dummy_destiny_id
    assert data.users[0].system == dummy_destiny_system
    assert data.users[0].character_id == dummy_character_id
    assert data.users[0].character_class == "Hunter"
    assert data.users[0].light_level == 1322
    assert data.users[0].completed is True
    assert data.users[0].kills == 22
    assert data.users[0].deaths == 1
    assert data.users[0].assists == 6
    assert data.users[0].time_played_seconds == 557

    input_model = DestinyLastInputModel(completed=False)
    r = await client.post(
        f"/destiny/activities/{dummy_discord_guild_id}/{dummy_discord_id}/last", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200

    input_model = DestinyLastInputModel(completed=True, character_class="Hunter")
    r = await client.post(
        f"/destiny/activities/{dummy_discord_guild_id}/{dummy_discord_id}/last", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200

    input_model = DestinyLastInputModel(completed=True, character_class="Warlock")
    r = await client.post(
        f"/destiny/activities/{dummy_discord_guild_id}/{dummy_discord_id}/last", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 409

    input_model = DestinyLastInputModel(completed=True, mode=4)
    r = await client.post(
        f"/destiny/activities/{dummy_discord_guild_id}/{dummy_discord_id}/last", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200

    input_model = DestinyLastInputModel(completed=True, mode=444)
    r = await client.post(
        f"/destiny/activities/{dummy_discord_guild_id}/{dummy_discord_id}/last", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 409

    input_model = DestinyLastInputModel(completed=True, mode=444, activity_ids=[dummy_activity_reference_id])
    r = await client.post(
        f"/destiny/activities/{dummy_discord_guild_id}/{dummy_discord_id}/last", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200

    input_model = DestinyLastInputModel(completed=True, mode=4, activity_ids=[1])
    r = await client.post(
        f"/destiny/activities/{dummy_discord_guild_id}/{dummy_discord_id}/last", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_activity(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    input_model = DestinyActivityInputModel(activity_ids=[dummy_activity_reference_id])
    r = await client.post(
        f"/destiny/activities/{dummy_discord_guild_id}/{dummy_discord_id}/activity",
        json=orjson.loads(input_model.json()),
    )
    assert r.status_code == 200
    data = DestinyActivityOutputModel.parse_obj(r.json())
    assert data.full_completions == 1
    assert data.cp_completions == 0
    assert data.kills == 22
    assert data.precision_kills == 10
    assert data.deaths == 1
    assert data.assists == 6
    assert data.time_spend.seconds == 557
    assert data.fastest.seconds == 917
    assert data.fastest_instance_id == dummy_instance_id
    assert data.average.seconds == 917


@pytest.mark.asyncio
async def test_get_grandmaster(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/activities/get/grandmaster")
    assert r.status_code == 200
    data = DestinyActivitiesModel.parse_obj(r.json())
    assert data.activities
    assert len(data.activities) == 3
    assert data.activities[0].name == "Grandmaster: All"
    assert data.activities[0].activity_ids == [8761236781273, 8761236781274]
    assert data.activities[1].name == "Grandmaster: Lake of Shadows"
    assert data.activities[1].description == "Grandmaster: Lake of Shadows"
    assert data.activities[1].activity_ids == [8761236781273]
    assert data.activities[1].mode == 46
    assert data.activities[2].name == "Grandmaster: NF"
    assert data.activities[2].activity_ids == [8761236781274]
