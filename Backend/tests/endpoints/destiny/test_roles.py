import pytest
from dummyData.insert import mock_request
from dummyData.static import *
from httpx import AsyncClient
from orjson import orjson
from pytest_mock import MockerFixture

from Shared.networkingSchemas.destiny.roles import (
    EarnedRoleModel,
    EarnedRolesModel,
    MissingRolesModel,
    RequirementActivityModel,
    RequirementIntegerModel,
    RoleDataModel,
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
    assert data.roles[0].role_id == 1
    assert data.roles[0].guild_id == dummy_discord_guild_id


@pytest.mark.asyncio
async def test_get_user(client: AsyncClient, mocker: MockerFixture):
    """Tests: get_user_all(), get_user_missing()"""

    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)

    # get the role
    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = RolesModel.parse_obj(r.json())
    my_role = data.roles[0]

    # =========================================================================
    # check all roles
    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/all")
    assert r.status_code == 200
    data = EarnedRolesModel.parse_obj(r.json())
    assert data.earned_but_replaced_by_higher_role == []
    assert data.not_earned == []
    assert data.earned
    assert len(data.earned) == 1
    assert data.earned[0].category == "Destiny Roles"
    assert data.earned[0].discord_role_id == 1

    # update the role a couple of times to see if it's still earned
    # check activity
    my_role.role_data.require_activity_completions = [
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

    # check wrong activity
    my_role.role_data.require_activity_completions = [
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

    # check collectible
    my_role.role_data.require_activity_completions = []
    my_role.role_data.require_collectibles = [RequirementIntegerModel(id=dummy_gotten_collectible_id)]
    r = await client.post(
        f"/destiny/roles/{dummy_discord_guild_id}/update/{my_role.role_id}", json=orjson.loads(my_role.json())
    )
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/all")
    assert r.status_code == 200
    data = EarnedRolesModel.parse_obj(r.json())
    assert len(data.earned) == 1

    # check wrong collectible
    my_role.role_data.require_collectibles = [RequirementIntegerModel(id=dummy_not_gotten_collectible_id)]
    r = await client.post(
        f"/destiny/roles/{dummy_discord_guild_id}/update/{my_role.role_id}", json=orjson.loads(my_role.json())
    )
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/all")
    assert r.status_code == 200
    data = EarnedRolesModel.parse_obj(r.json())
    assert len(data.not_earned) == 1

    # check record
    my_role.role_data.require_collectibles = []
    my_role.role_data.require_records = [RequirementIntegerModel(id=dummy_gotten_record_id)]
    r = await client.post(
        f"/destiny/roles/{dummy_discord_guild_id}/update/{my_role.role_id}", json=orjson.loads(my_role.json())
    )
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/all")
    assert r.status_code == 200
    data = EarnedRolesModel.parse_obj(r.json())
    assert len(data.earned) == 1

    # check wrong record
    my_role.role_data.require_records = [RequirementIntegerModel(id=dummy_not_gotten_record_id)]
    r = await client.post(
        f"/destiny/roles/{dummy_discord_guild_id}/update/{my_role.role_id}", json=orjson.loads(my_role.json())
    )
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/all")
    assert r.status_code == 200
    data = EarnedRolesModel.parse_obj(r.json())
    assert len(data.not_earned) == 1

    # =========================================================================
    # check specific role
    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/{my_role.role_id}")
    assert r.status_code == 200
    data = EarnedRoleModel.parse_obj(r.json())
    assert data.earned == RoleEnum.NOT_EARNED
    assert data.role == my_role
    assert data.user_role_data.require_activity_completions == []
    assert data.user_role_data.require_collectibles == []
    assert data.user_role_data.require_records == [False]
    assert data.user_role_data.require_role_ids == []

    # =========================================================================
    # check missing roles
    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/{dummy_discord_id}/get/missing")
    assert r.status_code == 200
    data = MissingRolesModel.parse_obj(r.json())
    assert data.acquirable
    assert len(data.acquirable) == 1
    assert data.acquirable[0].category == my_role.role_data.category
    assert data.acquirable[0].discord_role_id == my_role.role_id


@pytest.mark.asyncio
async def test_delete_role(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)

    input_model = RoleModel(
        role_id=2,
        guild_id=dummy_discord_guild_id,
        role_data=RoleDataModel(
            category="Destiny Roles",
            deprecated=False,
            acquirable=False,
            require_activity_completions=[],
            require_collectibles=[RequirementIntegerModel(id=dummy_gotten_collectible_id)],
            require_records=[RequirementIntegerModel(id=dummy_gotten_record_id)],
            require_role_ids=[],
            replaced_by_role_id=None,
        ),
    )
    r = await client.post(f"/destiny/roles/{dummy_discord_guild_id}/create", json=orjson.loads(input_model.json()))
    assert r.status_code == 200

    # delete
    r = await client.delete(f"/destiny/roles/{dummy_discord_guild_id}/delete/2")
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = RolesModel.parse_obj(r.json())
    for role in data.roles:
        assert role.role_id != 2
