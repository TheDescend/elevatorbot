import copy
import datetime
import json as json_lib
import os
import time
import unittest.mock
from typing import Optional
from urllib.parse import urlencode

from bungio.error import InvalidAuthentication
from bungio.models import AuthData, DestinyRecordDefinition
from dummyData.static import *
from httpx import AsyncClient
from orjson import orjson
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.bungio.client import get_bungio_client
from Backend.core.destiny.activities import DestinyActivities
from Backend.core.destiny.profile import DestinyProfile
from Backend.core.errors import CustomException
from Backend.crud import crud_activities, crud_activities_fail_to_get, discord_users
from Backend.database.models import DiscordUsers
from Backend.misc.cache import cache
from Backend.networking.schemas import WebResponse
from Shared.functions.helperFunctions import get_min_with_tz, get_now_with_tz, localize_datetime
from Shared.networkingSchemas.destiny.roles import (
    RequirementActivityModel,
    RequirementIntegerModel,
    RoleModel,
    RolesModel,
)
from Shared.networkingSchemas.misc.persistentMessages import (
    PersistentMessage,
    PersistentMessages,
    PersistentMessageUpsert,
)


class DummyClientResponse:
    status = 200

    @staticmethod
    async def text():
        return '<?xml version="1.0" encoding="utf-8" ?>\r\n<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:atom="http://www.w3.org/2005/Atom">\r\n\t<channel>\r\n\t\t<atom:icon>http://www.bungie.net/img/Bungie-Logo-PicLens-white.png</atom:icon>\r\n\t\t<title>Bungie.Net Content Feed</title>\r\n\t\t<link>http://www.bungie.net/en/rss/News?currentPage=1&amp;itemsPerPage=10&amp;category=All</link>\r\n\t\t<description>Data from the Bungie.Net News, Jobs, and other information</description>\r\n\t\t<language>en</language>\r\n\t\t<pubDate>Thu, 03 Mar 2022 10:40:02 GMT</pubDate>\r\n\t\t<docs>http://blogs.law.harvard.edu/tech/rss</docs>\r\n\t\t<generator>BlamDotNet RSS Generator</generator>\r\n\t\t<webMaster>webmaster@bungie.net (Bungie WebMaster)</webMaster>\r\n\t\t<atom:link rel="self" href="http://www.bungie.net:46000/en/rss/News"></atom:link>\r\n\t\t\t\t<atom:link rel="next" href="http://www.bungie.net/en/rss/News?currentPage=2&amp;itemsPerPage=10&amp;category=All"></atom:link>\r\n\t\t\t\t\t<item>\r\n\t\t\t\t<title>Community Focus - EpicDan22</title>\r\n\t\t\t\t<link>http://www.bungie.net/en/News/Article/51126</link>\r\n\t\t\t\t<pubDate>Fri, 25 Feb 2022 19:26:40 GMT</pubDate>\r\n\t\t\t\t<guid isPermaLink="false">BungieNet_ContentItem_51126</guid>\r\n\t\t\t\t<description></description>\r\n\t\t\t</item>\r\n\t</channel>\r\n</rss>'

    def release(self):
        pass


async def mock_request(
    self,
    method: str,
    route: str = None,
    str_or_url: str = None,
    params=None,
    *args,
    **kwargs,
) -> WebResponse | DummyClientResponse:
    if str_or_url:
        route = str_or_url

    if params is None:
        params = {}
    param_route = f"{route}?{urlencode(params)}"

    # handle elevator calls
    if param_route.startswith("http://None:None") or param_route.startswith("http://elevator:8080"):
        raise CustomException

    # handle rss feed checker calls, since they return xml
    if param_route == "https://www.bungie.net/en/rss/News?":
        return DummyClientResponse()

    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data.json"), "r", encoding="utf-8") as file:
        dummy_data: dict = json_lib.load(file)

        # capture the required route when this fails
        try:
            return WebResponse(get_now_with_tz(), 200, dummy_data[param_route], True)
        except KeyError as e:
            print("Tried to call this route, but it doesnt exist in the dummy data:")
            print(route)
            raise e


async def mock_elevator_post(self, *args, **kwargs):
    return True


MANIFEST_FIRST_UPDATE_CALL = True


async def mock_bungio_request(
    self,
    route: str,
    method: str,
    headers: dict,
    params: Optional[dict] = None,
    data: Optional[dict | list] = None,
    form_data: Optional[dict] = None,
    auth: Optional[AuthData] = None,
    use_ratelimiter: bool = True,
    *args,
    **kwargs,
) -> dict:
    global MANIFEST_FIRST_UPDATE_CALL

    if params is None:
        params = {}
    param_route = f"{route}?{urlencode(params)}"

    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data.json"), "r", encoding="utf-8") as file:
        dummy_data: dict = json_lib.load(file)

        # capture the required route when this fails
        try:
            data = dummy_data[param_route]

            # first manifest call needs to return a different version
            if MANIFEST_FIRST_UPDATE_CALL and param_route == "https://www.bungie.net/Platform/Destiny2/Manifest/?":
                MANIFEST_FIRST_UPDATE_CALL = False
                data = copy.deepcopy(data)
                data["version"] = "first_call_version"

            return data
        except KeyError as e:
            print("Tried to call this route, but it doesnt exist in the dummy data:")
            print(route)
            raise e


@unittest.mock.patch("Backend.networking.http.NetworkBase._request", mock_request)
@unittest.mock.patch("bungio.http.client.HttpClient._request", mock_bungio_request)
@unittest.mock.patch("Backend.networking.elevatorApi.ElevatorApi.post", mock_elevator_post)
async def insert_dummy_data(db: AsyncSession, client: AsyncClient):
    # create our registered destiny user
    token_data = AuthData(
        bungie_name=dummy_bungie_name,
        token=dummy_token,
        token_expiry=get_now_with_tz() + datetime.timedelta(days=1000),
        refresh_token=dummy_refresh_token,
        refresh_token_expiry=get_now_with_tz() + datetime.timedelta(days=1000),
        membership_id=dummy_destiny_id,
        membership_type=dummy_destiny_system,
    )
    result, user, discord_id, guild_id = await discord_users.insert_profile(
        db=db, auth=token_data, state=f"{dummy_discord_id}:{dummy_discord_guild_id}:{dummy_discord_channel_id}"
    )
    assert result.bungie_name == dummy_bungie_name
    assert user.destiny_id == dummy_destiny_id
    assert result.system == "BUNGIE_NEXT"
    assert discord_id == dummy_discord_id
    assert guild_id == dummy_discord_guild_id
    assert result.user_should_set_up_cross_save is False

    # create our registered destiny user without perms
    user_without_perms = DiscordUsers(
        discord_id=dummy_discord_id_without_perms,
        destiny_id=dummy_destiny_id_without_perms,
        system=dummy_destiny_system,
        bungie_name="X#1234",
        token="abc",
        refresh_token="def",
        token_expiry=get_now_with_tz() + datetime.timedelta(days=1000),
        refresh_token_expiry=get_now_with_tz() + datetime.timedelta(days=1000),
        signup_date=get_now_with_tz(),
        signup_server_id=dummy_discord_guild_id,
    )
    # noinspection PyProtectedMember
    await discord_users._insert(db=db, to_create=user_without_perms)

    # create a user that is deleted later
    user_to_delete = DiscordUsers(
        discord_id=99,
        destiny_id=98,
        system=dummy_destiny_system,
        bungie_name="Y#1234",
        token="abc",
        refresh_token="def",
        token_expiry=localize_datetime(datetime.datetime.fromtimestamp(int(time.time()) + 999999999)),
        refresh_token_expiry=localize_datetime(datetime.datetime.fromtimestamp(int(time.time()) + 999999999)),
        signup_date=get_now_with_tz(),
        signup_server_id=dummy_discord_guild_id,
    )
    # noinspection PyProtectedMember
    await discord_users._insert(db=db, to_create=user_to_delete)

    # =========================================================================
    # update their activities
    activities = DestinyActivities(db=db, user=user)
    await activities.update_activity_db()

    # noinspection PyProtectedMember
    assert user.activities_last_updated.day == 15
    assert user.activities_last_updated.month == 12
    assert dummy_instance_id in cache.saved_pgcrs

    fail = await crud_activities_fail_to_get.get_all(db=db)
    assert not fail

    pgcr = await crud_activities.get(db=db, instance_id=dummy_instance_id)
    assert pgcr is not None

    # try that again, it should not throw any error (which means it did not try to insert again)
    await activities.update_activity_db()

    # =========================================================================
    # insert collectibles
    profile = DestinyProfile(db=db, user=user)

    data = await profile.has_collectible(dummy_gotten_collectible_id)
    assert data is True

    data = await profile.has_collectible(dummy_not_gotten_collectible_id)
    assert data is False

    # test DB call
    data = await profile.has_collectible(dummy_gotten_collectible_id)
    assert data is True

    # =========================================================================
    # insert triumphs
    data = await profile.has_triumph(dummy_gotten_record_id)
    assert data.bool is True

    data = await profile.has_triumph(dummy_not_gotten_record_id)
    assert data.bool is False

    # test DB call
    data = await profile.has_triumph(dummy_gotten_record_id)
    assert data.bool is True

    # =========================================================================
    # insert persistent messages
    input_model = PersistentMessageUpsert(channel_id=dummy_persistent_lfg_channel_id, message_id=None)
    r = await client.post(
        f"/persistentMessages/{dummy_discord_guild_id}/upsert/lfg_channel", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = PersistentMessage.parse_obj(r.json())
    assert data.message_name == "lfg_channel"
    assert data.guild_id == dummy_discord_guild_id
    assert data.channel_id == dummy_persistent_lfg_channel_id
    assert data.message_id is None

    # does delete work?
    r = await client.delete(f"/persistentMessages/{dummy_discord_guild_id}/delete/all")
    assert r.status_code == 200
    r = await client.get(f"/persistentMessages/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = PersistentMessages.parse_obj(r.json())
    assert data.messages == []

    # now input them for real
    input_model = PersistentMessageUpsert(channel_id=dummy_persistent_lfg_channel_id, message_id=None)
    r = await client.post(
        f"/persistentMessages/{dummy_discord_guild_id}/upsert/lfg_channel", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200

    input_model = PersistentMessageUpsert(channel_id=dummy_persistent_lfg_voice_category_id, message_id=None)
    r = await client.post(
        f"/persistentMessages/{dummy_discord_guild_id}/upsert/lfg_voice_category", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = PersistentMessage.parse_obj(r.json())
    assert data.message_name == "lfg_voice_category"
    assert data.guild_id == dummy_discord_guild_id
    assert data.channel_id == dummy_persistent_lfg_voice_category_id
    assert data.message_id is None

    assert cache.persistent_messages

    # =========================================================================
    # insert roles
    input_model = RoleModel(
        role_id=1,
        guild_id=dummy_discord_guild_id,
        category="Destiny Roles",
        deprecated=False,
        acquirable=True,
    )
    r = await client.post(f"/destiny/roles/{dummy_discord_guild_id}/create", json=orjson.loads(input_model.json()))
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = RolesModel.parse_obj(r.json())
    assert len(data.roles) == 1
    assert data.roles[0].role_id == 1
    assert data.roles[0].guild_id == dummy_discord_guild_id

    # insert 2nd role
    input_model2 = copy.deepcopy(input_model)
    input_model2.role_id = 2
    input_model2.acquirable = False
    r = await client.post(f"/destiny/roles/{dummy_discord_guild_id}/create", json=orjson.loads(input_model2.json()))
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = RolesModel.parse_obj(r.json())
    assert len(data.roles) == 2

    # test update behaviour
    input_model.require_activity_completions = [RequirementActivityModel(allowed_activity_hashes=[1], count=1)]
    input_model.require_collectibles = [RequirementIntegerModel(bungie_id=1)]
    input_model.require_records = [RequirementIntegerModel(bungie_id=1)]
    input_model.require_role_ids = [2]
    input_model.replaced_by_role_id = 2
    r = await client.post(
        f"/destiny/roles/{dummy_discord_guild_id}/update/{input_model.role_id}", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = RolesModel.parse_obj(r.json())
    role = data.roles[1]
    assert role.require_activity_completions == input_model.require_activity_completions
    assert role.require_collectibles == input_model.require_collectibles
    assert role.require_records == input_model.require_records
    assert role.require_role_ids == input_model.require_role_ids
    assert role.replaced_by_role_id == input_model.replaced_by_role_id

    input_model.require_activity_completions = []
    input_model.require_collectibles = []
    input_model.require_records = []
    input_model.require_role_ids = []
    input_model.replaced_by_role_id = None
    r = await client.post(
        f"/destiny/roles/{dummy_discord_guild_id}/update/{input_model.role_id}", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = RolesModel.parse_obj(r.json())
    role = data.roles[1]
    assert role.require_activity_completions == input_model.require_activity_completions
    assert role.require_collectibles == input_model.require_collectibles
    assert role.require_records == input_model.require_records
    assert role.require_role_ids == input_model.require_role_ids
    assert role.replaced_by_role_id == input_model.replaced_by_role_id

    # delete all roles
    r = await client.delete(f"/destiny/roles/{dummy_discord_guild_id}/delete/all")
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = RolesModel.parse_obj(r.json())
    assert data.roles == []

    # now test cascade behaviour
    r = await client.post(f"/destiny/roles/{dummy_discord_guild_id}/create", json=orjson.loads(input_model.json()))
    assert r.status_code == 200

    input_model2.require_role_ids = [1]
    r = await client.post(f"/destiny/roles/{dummy_discord_guild_id}/create", json=orjson.loads(input_model2.json()))
    assert r.status_code == 200
    assert cache.roles[2].requirement_require_roles
    assert len(cache.roles[2].requirement_require_roles) == 1
    assert cache.roles[2].requirement_require_roles[0].role_id == 1

    input_model3 = copy.deepcopy(input_model)
    input_model3.role_id = 3
    input_model3.replaced_by_role_id = 2
    input_model3.acquirable = False
    r = await client.post(f"/destiny/roles/{dummy_discord_guild_id}/create", json=orjson.loads(input_model3.json()))
    assert r.status_code == 200
    # noinspection PyProtectedMember
    assert cache.roles[3]._replaced_by_role_id == 2
    assert cache.roles[3].requirement_replaced_by_role
    assert cache.roles[3].requirement_replaced_by_role.role_id == 2

    # deleting role 3 should not delete role 2
    r = await client.delete(f"/destiny/roles/{dummy_discord_guild_id}/delete/3")
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = RolesModel.parse_obj(r.json())
    assert len(data.roles) == 2
    for role in data.roles:
        assert role.role_id != 3

    # deleting role 1 should delete role 1 and 2
    r = await client.post(f"/destiny/roles/{dummy_discord_guild_id}/create", json=orjson.loads(input_model3.json()))
    assert r.status_code == 200

    r = await client.delete(f"/destiny/roles/{dummy_discord_guild_id}/delete/1")
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = RolesModel.parse_obj(r.json())
    assert len(data.roles) == 1
    for role in data.roles:
        assert role.role_id != 1
        assert role.role_id != 2

    # deleting role 2 should not delete role 1, only role 2
    r = await client.post(f"/destiny/roles/{dummy_discord_guild_id}/create", json=orjson.loads(input_model.json()))
    assert r.status_code == 200
    r = await client.post(f"/destiny/roles/{dummy_discord_guild_id}/create", json=orjson.loads(input_model2.json()))
    assert r.status_code == 200

    r = await client.delete(f"/destiny/roles/{dummy_discord_guild_id}/delete/2")
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = RolesModel.parse_obj(r.json())
    assert len(data.roles) == 2
    for role in data.roles:
        assert role.role_id != 2

    # check that role 3 is no longer replaced by 2
    # noinspection PyProtectedMember
    assert cache.roles[3]._replaced_by_role_id is None
    assert cache.roles[3].requirement_replaced_by_role is None
    assert len(cache.roles) == 2

    assert dummy_discord_guild_id in cache.guild_roles
    assert len(cache.guild_roles[dummy_discord_guild_id]) == 2
    for role in cache.guild_roles[dummy_discord_guild_id]:
        assert role.role_id != 2

    # fetch some manifest data to force an update
    await get_bungio_client().manifest.fetch_all(manifest_class=DestinyRecordDefinition)
