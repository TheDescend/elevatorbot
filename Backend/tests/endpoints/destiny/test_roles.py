import copy

import pytest
from dummyData.insert import mock_request
from dummyData.static import *
from httpx import AsyncClient
from orjson import orjson
from pytest_mock import MockerFixture

from Backend.misc.cache import cache
from Shared.networkingSchemas.destiny.roles import (
    EarnedRoleModel,
    EarnedRolesModel,
    MissingRolesModel,
    RequirementActivityModel,
    RequirementIntegerModel,
    RoleEnum,
    RoleModel,
    RolesModel,
)


@pytest.mark.asyncio
async def test_get_all(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = RolesModel.parse_obj(r.json())
    assert data.roles
    assert len(data.roles) > 0

    found = None
    for role in data.roles:
        if role.role_id == 1:
            found = role
            break

    assert found is not None
    assert found.guild_id == dummy_discord_guild_id


@pytest.mark.asyncio
async def test_get_user(client: AsyncClient, mocker: MockerFixture):
    """Tests: get_user_all(), get_user_missing()"""

    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)

    # get the role
    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = RolesModel.parse_obj(r.json())

    # get role with id 1
    my_role: RoleModel | None = None
    for role in data.roles:
        if role.role_id == 1:
            my_role = role
            break
    assert my_role is not None

    # =========================================================================
    # check all roles
    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/all")
    assert r.status_code == 200
    data = EarnedRolesModel.parse_obj(r.json())
    assert data.earned
    assert len(data.earned) == 1
    assert data.earned[0].category == "Destiny Roles"
    assert data.earned[0].discord_role_id == 1
    assert len(data.not_earned) == 0
    assert len(data.earned_but_replaced_by_higher_role) == 0

    # update the role a couple of times to see if it's still earned
    # check activity
    my_role.require_activity_completions = [
        RequirementActivityModel(
            allowed_activity_hashes=[dummy_activity_reference_id], count=1, maximum_allowed_players=1
        )
    ]
    r = await client.post(
        f"/destiny/roles/{dummy_discord_guild_id}/update/{my_role.role_id}", json=orjson.loads(my_role.json())
    )
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/all")
    assert r.status_code == 200
    data = EarnedRolesModel.parse_obj(r.json())
    assert len(data.earned) == 1
    assert len(data.not_earned) == 0
    assert len(data.earned_but_replaced_by_higher_role) == 0

    # check wrong activity
    my_role.require_activity_completions = [
        RequirementActivityModel(
            allowed_activity_hashes=[dummy_activity_reference_id], count=2, maximum_allowed_players=1
        )
    ]
    r = await client.post(
        f"/destiny/roles/{dummy_discord_guild_id}/update/{my_role.role_id}", json=orjson.loads(my_role.json())
    )
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/all")
    assert r.status_code == 200
    data = EarnedRolesModel.parse_obj(r.json())
    assert len(data.not_earned) == 1
    assert len(data.earned) == 0
    assert len(data.earned_but_replaced_by_higher_role) == 0

    # check collectible
    my_role.require_activity_completions = []
    my_role.require_collectibles = [RequirementIntegerModel(bungie_id=dummy_gotten_collectible_id)]
    r = await client.post(
        f"/destiny/roles/{dummy_discord_guild_id}/update/{my_role.role_id}", json=orjson.loads(my_role.json())
    )
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/all")
    assert r.status_code == 200
    data = EarnedRolesModel.parse_obj(r.json())
    assert len(data.earned) == 1
    assert len(data.not_earned) == 0
    assert len(data.earned_but_replaced_by_higher_role) == 0

    # check wrong collectible
    my_role.require_collectibles = [RequirementIntegerModel(bungie_id=dummy_not_gotten_collectible_id)]
    r = await client.post(
        f"/destiny/roles/{dummy_discord_guild_id}/update/{my_role.role_id}", json=orjson.loads(my_role.json())
    )
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/all")
    assert r.status_code == 200
    data = EarnedRolesModel.parse_obj(r.json())
    assert len(data.not_earned) == 1
    assert len(data.earned) == 0
    assert len(data.earned_but_replaced_by_higher_role) == 0

    # check record
    my_role.require_collectibles = []
    my_role.require_records = [RequirementIntegerModel(bungie_id=dummy_gotten_record_id)]
    r = await client.post(
        f"/destiny/roles/{dummy_discord_guild_id}/update/{my_role.role_id}", json=orjson.loads(my_role.json())
    )
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/all")
    assert r.status_code == 200
    data = EarnedRolesModel.parse_obj(r.json())
    assert len(data.earned) == 1
    assert len(data.not_earned) == 0
    assert len(data.earned_but_replaced_by_higher_role) == 0

    # check wrong record
    my_role.require_records = [RequirementIntegerModel(bungie_id=dummy_not_gotten_record_id)]
    r = await client.post(
        f"/destiny/roles/{dummy_discord_guild_id}/update/{my_role.role_id}", json=orjson.loads(my_role.json())
    )
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/all")
    assert r.status_code == 200
    data = EarnedRolesModel.parse_obj(r.json())
    assert len(data.not_earned) == 1
    assert len(data.earned) == 0
    assert len(data.earned_but_replaced_by_higher_role) == 0

    # check not earned required role
    my_role.require_records = []
    new_role = copy.deepcopy(my_role)
    new_role.require_records = [RequirementIntegerModel(bungie_id=dummy_not_gotten_record_id)]
    new_role.role_id = 50
    r = await client.post(f"/destiny/roles/{dummy_discord_guild_id}/create", json=orjson.loads(new_role.json()))
    assert r.status_code == 200

    my_role.require_role_ids = [50]
    r = await client.post(
        f"/destiny/roles/{dummy_discord_guild_id}/update/{my_role.role_id}", json=orjson.loads(my_role.json())
    )
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/all")
    assert r.status_code == 200
    data = EarnedRolesModel.parse_obj(r.json())
    assert len(data.not_earned) == 2
    assert len(data.earned) == 0
    assert len(data.earned_but_replaced_by_higher_role) == 0

    # check earned required role
    new_role.require_records = []
    r = await client.post(
        f"/destiny/roles/{dummy_discord_guild_id}/update/{new_role.role_id}", json=orjson.loads(new_role.json())
    )
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/all")
    assert r.status_code == 200
    data = EarnedRolesModel.parse_obj(r.json())
    assert len(data.not_earned) == 0
    assert len(data.earned) == 2
    assert len(data.earned_but_replaced_by_higher_role) == 0

    # check replaced by role
    new_role.replaced_by_role_id = my_role.role_id
    r = await client.post(
        f"/destiny/roles/{dummy_discord_guild_id}/update/{new_role.role_id}", json=orjson.loads(new_role.json())
    )
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/all")
    assert r.status_code == 200
    data = EarnedRolesModel.parse_obj(r.json())
    assert len(data.not_earned) == 0
    assert len(data.earned) == 1
    assert len(data.earned_but_replaced_by_higher_role) == 1

    # =========================================================================
    # check specific role
    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/{my_role.role_id}")
    assert r.status_code == 200
    data = EarnedRoleModel.parse_obj(r.json())
    assert data.earned == RoleEnum.EARNED
    assert data.role == my_role
    assert data.user_role_data.require_activity_completions == []
    assert data.user_role_data.require_collectibles == []
    assert data.user_role_data.require_records == []
    assert data.user_role_data.require_role_ids == [True]

    my_role.require_activity_completions = [
        RequirementActivityModel(
            allowed_activity_hashes=[dummy_activity_reference_id], count=1, maximum_allowed_players=1
        )
    ]
    my_role.require_collectibles = [RequirementIntegerModel(bungie_id=dummy_gotten_collectible_id)]
    my_role.require_records = [RequirementIntegerModel(bungie_id=dummy_gotten_record_id)]
    my_role.replaced_by_role_id = None
    r = await client.post(
        f"/destiny/roles/{dummy_discord_guild_id}/update/{my_role.role_id}", json=orjson.loads(my_role.json())
    )
    assert r.status_code == 200
    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/{my_role.role_id}")
    assert r.status_code == 200
    data = EarnedRoleModel.parse_obj(r.json())
    assert data.earned == RoleEnum.EARNED
    assert data.role == my_role
    assert data.user_role_data.require_activity_completions == ["1 / 1"]
    assert data.user_role_data.require_collectibles == [True]
    assert data.user_role_data.require_records == [True]
    assert data.user_role_data.require_role_ids == [True]

    my_role.require_activity_completions.append(
        RequirementActivityModel(
            allowed_activity_hashes=[dummy_activity_reference_id], count=2, maximum_allowed_players=1
        )
    )
    my_role.require_collectibles.append(RequirementIntegerModel(bungie_id=dummy_not_gotten_collectible_id))
    my_role.require_records.append(RequirementIntegerModel(bungie_id=dummy_not_gotten_record_id))
    r = await client.post(
        f"/destiny/roles/{dummy_discord_guild_id}/update/{my_role.role_id}", json=orjson.loads(my_role.json())
    )
    assert r.status_code == 200
    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/{my_role.role_id}")
    assert r.status_code == 200
    data = EarnedRoleModel.parse_obj(r.json())
    assert data.earned == RoleEnum.NOT_EARNED
    assert data.role == my_role
    assert data.user_role_data.require_activity_completions == ["1 / 1", "1 / 2"]
    assert data.user_role_data.require_collectibles == [True, False]
    assert data.user_role_data.require_records == [True, False]
    assert data.user_role_data.require_role_ids == [True]

    # =========================================================================
    # check missing roles
    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/missing")
    assert r.status_code == 200
    data = MissingRolesModel.parse_obj(r.json())
    assert data.acquirable
    assert len(data.acquirable) == 1
    assert data.acquirable[0].category == my_role.category
    assert data.acquirable[0].discord_role_id == my_role.role_id


@pytest.mark.asyncio
async def test_delete_role(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)

    input_model = RoleModel(
        role_id=100,
        guild_id=dummy_discord_guild_id,
        category="Destiny Roles",
        deprecated=False,
        acquirable=False,
        require_activity_completions=[],
        require_collectibles=[RequirementIntegerModel(bungie_id=dummy_gotten_collectible_id)],
        require_records=[RequirementIntegerModel(bungie_id=dummy_gotten_record_id)],
        require_role_ids=[],
        replaced_by_role_id=None,
    )
    r = await client.post(f"/destiny/roles/{dummy_discord_guild_id}/create", json=orjson.loads(input_model.json()))
    assert r.status_code == 200

    # delete
    r = await client.delete(f"/destiny/roles/{dummy_discord_guild_id}/delete/100")
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = RolesModel.parse_obj(r.json())
    for role in data.roles:
        assert role.role_id != 100
