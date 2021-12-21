import pytest
from dummyData.insert import mock_request
from dummyData.static import *
from httpx import AsyncClient
from orjson import orjson
from pytest_mock import MockerFixture

from NetworkingSchemas.misc.persistentMessages import (
    PersistentMessage,
    PersistentMessageDeleteInput,
    PersistentMessages,
    PersistentMessageUpsert,
)


@pytest.mark.asyncio
async def test_get_all(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/persistentMessages/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = PersistentMessages.parse_obj(r.json())
    assert data.messages != []
    assert len(data.messages) >= 2
    assert data.messages[0].message_name == "lfg_channel"
    assert data.messages[0].guild_id == dummy_discord_guild_id
    assert data.messages[0].channel_id == dummy_persistent_lfg_channel_id
    assert data.messages[0].message_id is None
    assert data.messages[1].message_name == "lfg_voice_category"
    assert data.messages[1].guild_id == dummy_discord_guild_id
    assert data.messages[1].channel_id == dummy_persistent_lfg_voice_category_id
    assert data.messages[1].message_id is None


@pytest.mark.asyncio
async def test_get(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/persistentMessages/{dummy_discord_guild_id}/get/lfg_channel")
    assert r.status_code == 200
    data = PersistentMessage.parse_obj(r.json())
    assert data.message_name == "lfg_channel"
    assert data.guild_id == dummy_discord_guild_id
    assert data.channel_id == dummy_persistent_lfg_channel_id
    assert data.message_id is None


@pytest.mark.asyncio
async def test_delete(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    # use the message_name
    delete_model = PersistentMessageDeleteInput(message_name="to_delete")
    await assert_delete_message(client=client, delete_model=delete_model)

    # use the channel_id
    delete_model = PersistentMessageDeleteInput(channel_id=1)
    await assert_delete_message(client=client, delete_model=delete_model)

    # use the message_id
    delete_model = PersistentMessageDeleteInput(message_id=2)
    await assert_delete_message(client=client, delete_model=delete_model)


async def assert_delete_message(client: AsyncClient, delete_model: PersistentMessageDeleteInput):
    """Tests that delete() works just fine"""

    # delete non existing message
    r = await client.post(
        f"/persistentMessages/{dummy_discord_guild_id}/delete", json=orjson.loads(delete_model.json())
    )
    assert r.status_code == 409
    assert r.json()["error"] == "PersistentMessageNotExist"

    # insert new message
    input_model = PersistentMessageUpsert(channel_id=1, message_id=2)
    r = await client.post(
        f"/persistentMessages/{dummy_discord_guild_id}/upsert/to_delete", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200

    # get it
    r = await client.get(f"/persistentMessages/{dummy_discord_guild_id}/get/to_delete")
    assert r.status_code == 200

    # delete it
    r = await client.post(
        f"/persistentMessages/{dummy_discord_guild_id}/delete", json=orjson.loads(delete_model.json())
    )
    assert r.status_code == 200

    # get it
    r = await client.get(f"/persistentMessages/{dummy_discord_guild_id}/get/to_delete")
    assert r.status_code == 409
    assert r.json()["error"] == "PersistentMessageNotExist"
