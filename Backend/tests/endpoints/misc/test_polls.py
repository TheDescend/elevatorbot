import pytest
from dummyData.insert import mock_request
from dummyData.static import *
from httpx import AsyncClient
from orjson import orjson
from pytest_mock import MockerFixture

from Shared.NetworkingSchemas.misc.polls import PollInsertSchema, PollSchema, PollUserInputSchema


@pytest.mark.asyncio
async def test_polls(client: AsyncClient, mocker: MockerFixture):
    """This tests all function in the file, because insert() needs to be called first"""

    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    # =====================================================================
    # insert
    # no poll exists yet
    r = await client.get(f"/polls/{dummy_discord_guild_id}/{dummy_discord_id}/get/1")
    assert r.status_code == 409
    assert r.json()["error"] == "PollNotExist"

    # insert
    input_model = PollInsertSchema(
        name="My Poll",
        description="Nothing here",
        data=dict,
        author_id=dummy_discord_id,
        guild_id=dummy_discord_id,
        channel_id=dummy_discord_channel_id,
        message_id=1,
    )
    r = await client.post(
        f"/polls/{dummy_discord_guild_id}/{dummy_discord_id}/insert", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = PollSchema.parse_obj(r.json())
    assert_poll(data)
    assert data.choices == []

    # =====================================================================
    # get
    r = await client.get(f"/polls/{dummy_discord_guild_id}/{dummy_discord_id}/get/1")
    assert r.status_code == 200
    data = PollSchema.parse_obj(r.json())
    assert_poll(data)
    assert data.choices == []

    # =====================================================================
    # update -> user_input
    # this is special, in that a user input serves as the update as well
    update_model = PollUserInputSchema(choice_name="choice_1")
    r = await client.post(
        f"/polls/{dummy_discord_guild_id}/{dummy_discord_id}/1/user_input", json=orjson.loads(update_model.json())
    )
    assert r.status_code == 200
    data = PollSchema.parse_obj(r.json())
    assert_poll(data)
    assert data.choices != []
    assert len(data.choices) == 1
    assert data.choices[0].name == "choice_1"
    assert data.choices[0].discord_ids == [dummy_discord_id]

    # change their choice
    update_model = PollUserInputSchema(choice_name="choice_2")
    r = await client.post(
        f"/polls/{dummy_discord_guild_id}/{dummy_discord_id}/1/user_input", json=orjson.loads(update_model.json())
    )
    assert r.status_code == 200
    data = PollSchema.parse_obj(r.json())
    assert_poll(data)
    assert data.choices != []
    assert len(data.choices) == 2
    assert data.choices[0].name == "choice_1"
    assert data.choices[0].discord_ids == []
    assert data.choices[1].name == "choice_2"
    assert data.choices[1].discord_ids == [dummy_discord_id]

    # =====================================================================
    # delete option without perms
    r = await client.delete(
        f"/polls/{dummy_discord_guild_id}/{dummy_discord_id_without_perms}/1/delete_option/choice_1"
    )
    assert r.status_code == 409
    assert r.json()["error"] == "PollNoPermission"

    # delete option
    r = await client.delete(f"/polls/{dummy_discord_guild_id}/{dummy_discord_id}/1/delete_option/choice_1")
    assert r.status_code == 200
    data = PollSchema.parse_obj(r.json())
    assert_poll(data)
    assert len(data.choices) == 1
    assert data.choices[0].name == "choice_2"

    # delete not existing option
    r = await client.delete(f"/polls/{dummy_discord_guild_id}/{dummy_discord_id}/1/delete_option/choice_1")
    assert r.status_code == 409
    assert r.json()["error"] == "PollOptionNotExist"

    # =====================================================================
    # delete without perms
    r = await client.delete(f"/polls/{dummy_discord_guild_id}/{dummy_discord_id_without_perms}/1/delete")
    assert r.status_code == 409
    assert r.json()["error"] == "PollNoPermission"

    # delete
    r = await client.delete(f"/polls/{dummy_discord_guild_id}/{dummy_discord_id}/1/delete")
    assert r.status_code == 200
    data = PollSchema.parse_obj(r.json())
    assert_poll(data)

    # no poll exists again
    r = await client.get(f"/polls/{dummy_discord_guild_id}/{dummy_discord_id}/get/1")
    assert r.status_code == 409
    assert r.json()["error"] == "PollNotExist"

    # =====================================================================
    # delete all
    # insert again
    r = await client.post(
        f"/polls/{dummy_discord_guild_id}/{dummy_discord_id}/insert", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200

    # delete all
    r = await client.delete(f"/polls/{dummy_discord_guild_id}/delete/all")
    assert r.status_code == 200

    # no poll exists again
    r = await client.get(f"/polls/{dummy_discord_guild_id}/{dummy_discord_id}/get/1")
    assert r.status_code == 409
    assert r.json()["error"] == "PollNotExist"


def assert_poll(data: PollSchema):
    """Check that the poll is OK"""

    assert data.id == 1
    assert data.name == "My Poll"
    assert data.description == "Nothing here"
    assert data.author_id == dummy_discord_id
    assert data.guild_id == dummy_discord_id
    assert data.channel_id == dummy_discord_channel_id
    assert data.message_id == 1
