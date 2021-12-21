import datetime

import pytest
from dummyData.insert import mock_request
from dummyData.static import *
from httpx import AsyncClient
from orjson import orjson
from pytest_mock import MockerFixture

from Backend.misc.helperFunctions import get_now_with_tz
from NetworkingSchemas.destiny.weapons import (
    DestinyTopWeaponModel,
    DestinyTopWeaponsInputModel,
    DestinyTopWeaponsModel,
    DestinyTopWeaponsStatInputModelEnum,
    DestinyWeaponsModel,
    DestinyWeaponStatsInputModel,
    DestinyWeaponStatsModel,
)


@pytest.mark.asyncio
async def test_get_all(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/weapons/get/all")
    assert r.status_code == 200
    data = DestinyWeaponsModel.parse_obj(r.json())
    assert data.weapons
    assert len(data.weapons) == 3
    assert data.weapons[0].name == "kinetic"
    assert data.weapons[0].description == ""
    assert data.weapons[0].flavor_text == "Oh my gawd"
    assert data.weapons[0].weapon_type == "Trace Rifle"
    assert data.weapons[0].weapon_slot == "Kinetic"
    assert data.weapons[0].damage_type == "Stasis"
    assert data.weapons[0].ammo_type == "Special"
    assert data.weapons[0].reference_ids == [61]
    assert data.weapons[2].reference_ids == [63, 64]


@pytest.mark.asyncio
async def test_get_top(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    # prec kills
    input_model = DestinyTopWeaponsInputModel(
        stat=DestinyTopWeaponsStatInputModelEnum.PRECISION_KILLS, how_many_per_slot=10
    )
    r = await client.post(
        f"/destiny/weapons/{dummy_discord_guild_id}/{dummy_discord_id}/top", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTopWeaponsModel.parse_obj(r.json())
    assert_weapon_ranking(data)
    assert data.kinetic[0].stat_value == 10

    # kills
    input_model = DestinyTopWeaponsInputModel(stat=DestinyTopWeaponsStatInputModelEnum.KILLS, how_many_per_slot=10)
    r = await client.post(
        f"/destiny/weapons/{dummy_discord_guild_id}/{dummy_discord_id}/top", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTopWeaponsModel.parse_obj(r.json())
    assert_weapon_ranking(data)
    assert data.kinetic[0].stat_value == 100

    # try a very variations
    input_model.weapon_type = 25
    r = await client.post(
        f"/destiny/weapons/{dummy_discord_guild_id}/{dummy_discord_id}/top", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTopWeaponsModel.parse_obj(r.json())
    assert_weapon_ranking(data)

    input_model.damage_type = 6
    r = await client.post(
        f"/destiny/weapons/{dummy_discord_guild_id}/{dummy_discord_id}/top", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTopWeaponsModel.parse_obj(r.json())
    assert_weapon_ranking(data)

    input_model.character_class = "Hunter"
    r = await client.post(
        f"/destiny/weapons/{dummy_discord_guild_id}/{dummy_discord_id}/top", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTopWeaponsModel.parse_obj(r.json())
    assert_weapon_ranking(data)

    input_model.character_ids = [dummy_character_id]
    r = await client.post(
        f"/destiny/weapons/{dummy_discord_guild_id}/{dummy_discord_id}/top", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTopWeaponsModel.parse_obj(r.json())
    assert_weapon_ranking(data)

    input_model.mode = 4
    r = await client.post(
        f"/destiny/weapons/{dummy_discord_guild_id}/{dummy_discord_id}/top", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTopWeaponsModel.parse_obj(r.json())
    assert_weapon_ranking(data)

    input_model.activity_hashes = [dummy_activity_reference_id]
    r = await client.post(
        f"/destiny/weapons/{dummy_discord_guild_id}/{dummy_discord_id}/top", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTopWeaponsModel.parse_obj(r.json())
    assert_weapon_ranking(data)

    input_model.end_time = get_now_with_tz()
    r = await client.post(
        f"/destiny/weapons/{dummy_discord_guild_id}/{dummy_discord_id}/top", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTopWeaponsModel.parse_obj(r.json())
    assert_weapon_ranking(data)

    # try something that should not work
    input_model.activity_hashes = [1234]
    r = await client.post(
        f"/destiny/weapons/{dummy_discord_guild_id}/{dummy_discord_id}/top", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTopWeaponsModel.parse_obj(r.json())
    assert data.kinetic == []


@pytest.mark.asyncio
async def test_get_weapon(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    input_model = DestinyWeaponStatsInputModel(weapon_ids=[61])
    r = await client.post(
        f"/destiny/weapons/{dummy_discord_guild_id}/{dummy_discord_id}/weapon", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyWeaponStatsModel.parse_obj(r.json())
    assert_weapon_stats(data)

    # test a few variations
    input_model.character_class = "Hunter"
    r = await client.post(
        f"/destiny/weapons/{dummy_discord_guild_id}/{dummy_discord_id}/weapon", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyWeaponStatsModel.parse_obj(r.json())
    assert_weapon_stats(data)

    input_model.character_ids = [dummy_character_id]
    r = await client.post(
        f"/destiny/weapons/{dummy_discord_guild_id}/{dummy_discord_id}/weapon", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyWeaponStatsModel.parse_obj(r.json())
    assert_weapon_stats(data)

    input_model.mode = 4
    r = await client.post(
        f"/destiny/weapons/{dummy_discord_guild_id}/{dummy_discord_id}/weapon", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyWeaponStatsModel.parse_obj(r.json())
    assert_weapon_stats(data)

    input_model.activity_hashes = {dummy_activity_reference_id}
    r = await client.post(
        f"/destiny/weapons/{dummy_discord_guild_id}/{dummy_discord_id}/weapon", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyWeaponStatsModel.parse_obj(r.json())
    assert_weapon_stats(data)

    input_model.end_time = get_now_with_tz()
    r = await client.post(
        f"/destiny/weapons/{dummy_discord_guild_id}/{dummy_discord_id}/weapon", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyWeaponStatsModel.parse_obj(r.json())
    assert_weapon_stats(data)

    # try something that should not work
    input_model.character_class = "Warlock"
    r = await client.post(
        f"/destiny/weapons/{dummy_discord_guild_id}/{dummy_discord_id}/weapon", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 409
    assert r.json()["error"] == "WeaponUnused"


def assert_weapon_ranking(data: DestinyTopWeaponsModel):
    """Tests that the weapon is OK"""

    assert data.energy == []
    assert data.power == []
    assert data.kinetic != []
    assert len(data.kinetic) == 1
    assert data.kinetic[0].ranking == 1
    assert data.kinetic[0].weapon_ids == [61]
    assert data.kinetic[0].weapon_name == "kinetic"
    assert data.kinetic[0].weapon_type == "Trace Rifle"
    assert data.kinetic[0].weapon_tier == "Common"
    assert data.kinetic[0].weapon_damage_type == "Stasis"
    assert data.kinetic[0].weapon_ammo_type == "Special"


def assert_weapon_stats(data: DestinyWeaponStatsModel):
    """Tests that the weapon is OK"""

    assert data.total_kills == 100
    assert data.total_precision_kills == 10
    assert data.total_activities == 1
    assert data.best_kills == 100
    assert data.best_kills_activity_name == dummy_activity_name
    assert data.best_kills_activity_id == dummy_instance_id
    assert data.best_kills_date.day == 15
    assert data.best_kills_date.month == 12
    assert data.best_kills_date.year == 2021
