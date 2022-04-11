import copy
import datetime
import json as json_lib
import os
import time
import unittest.mock
from urllib.parse import urlencode

from dummyData.static import *
from httpx import AsyncClient
from orjson import orjson
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.destiny.activities import DestinyActivities
from Backend.core.destiny.manifest import DestinyManifest
from Backend.core.destiny.profile import DestinyProfile
from Backend.core.errors import CustomException
from Backend.crud import crud_activities, crud_activities_fail_to_get, destiny_manifest, discord_users
from Backend.database.models import (
    DestinyActivityDefinition,
    DestinyActivityModeDefinition,
    DestinyActivityTypeDefinition,
    DestinyCollectibleDefinition,
    DestinyInventoryBucketDefinition,
    DestinyInventoryItemDefinition,
    DestinyLoreDefinition,
    DestinyPresentationNodeDefinition,
    DestinyRecordDefinition,
    DestinySeasonPassDefinition,
    DiscordUsers,
)
from Backend.misc.cache import cache
from Backend.networking.schemas import WebResponse
from Shared.functions.helperFunctions import get_now_with_tz, localize_datetime
from Shared.networkingSchemas.destiny.roles import RequirementIntegerModel, RoleModel, RolesModel
from Shared.networkingSchemas.misc.auth import BungieTokenInput
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


@unittest.mock.patch("Backend.networking.http.NetworkBase._request", mock_request)
@unittest.mock.patch("Backend.networking.elevatorApi.ElevatorApi.post", mock_elevator_post)
async def insert_dummy_data(db: AsyncSession, client: AsyncClient):
    # create our registered destiny user
    token_data = BungieTokenInput(
        access_token=dummy_token,
        token_type="EMPTY",
        expires_in=999999999,
        refresh_token=dummy_refresh_token,
        refresh_expires_in=999999999,
        membership_id=dummy_destiny_id,
        state=f"{dummy_discord_id}:{dummy_discord_guild_id}:{dummy_discord_channel_id}",
    )
    result, user, discord_id, guild_id = await discord_users.insert_profile(db=db, bungie_token=token_data)
    assert result.bungie_name == dummy_bungie_name
    assert user.destiny_id == dummy_destiny_id
    assert result.system == "PYTEST"
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
        token_expiry=localize_datetime(datetime.datetime.fromtimestamp(int(time.time()) + 999999999)),
        refresh_token_expiry=localize_datetime(datetime.datetime.fromtimestamp(int(time.time()) + 999999999)),
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
    assert activities._full_character_list == [{"char_id": 666, "deleted": False}]
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
    assert data.objectives[0].bool is True
    assert data.objectives[1].bool is False

    # test DB call
    data = await profile.has_triumph(dummy_gotten_record_id)
    assert data.bool is True

    # =========================================================================
    # insert manifest data
    manifest = DestinyManifest(db=db)
    await manifest.update()

    # check if the entries are ok
    version = await destiny_manifest.get_version(db=db)
    assert version.version == "99687.21.11.15.1900-1-bnet.41786"

    data = await destiny_manifest.get(db=db, table=DestinyActivityDefinition, primary_key=dummy_activity_reference_id)
    assert data.description == 'Enter the realm of the Nine and ask the question: "What is the nature of the Darkness?"'
    assert data.name == "Prophecy"
    assert data.activity_light_level == 1040
    assert data.destination_hash == 1553550479
    assert data.place_hash == 3747705955
    assert data.activity_type_hash == 2043403989
    assert data.is_pvp is False
    assert data.direct_activity_mode_hash == 2043403989
    assert data.direct_activity_mode_type == 4
    assert data.activity_mode_hashes == [2043403989]
    assert data.activity_mode_types == [4]
    assert data.max_players == 3
    assert data.matchmade is False

    data = await destiny_manifest.get(db=db, table=DestinyActivityTypeDefinition, primary_key=2043403989)
    assert data.description == "Form a fireteam of six and brave the strange and powerful realms of our enemies."
    assert data.name == "Raid"

    data = await destiny_manifest.get(db=db, table=DestinyActivityModeDefinition, primary_key=2043403989)
    assert data.parent_hashes == [1164760493]
    assert data.mode_type == 4
    assert data.description == "All of your Raid stats rolled into one."
    assert data.name == "Raid"
    assert data.activity_mode_category == 1
    assert data.is_team_based is False
    assert data.friendly_name == "raid"
    assert data.display is True
    assert data.redacted is False

    data = await destiny_manifest.get(
        db=db, table=DestinyCollectibleDefinition, primary_key=dummy_gotten_collectible_id
    )
    assert data.description == ""
    assert data.name == "Earned Collectible"
    assert data.source_hash == 897576623
    assert data.item_hash == 2094233929
    assert data.parent_node_hashes == [1633867910]

    data = await destiny_manifest.get(db=db, table=DestinyInventoryItemDefinition, primary_key=41)
    assert data.description == ""
    assert data.name == "Collectible"
    assert data.flavor_text == ""
    assert data.item_type == 2
    assert data.item_sub_type == 27
    assert data.class_type == 1
    assert data.bucket_type_hash == 3551918588
    assert data.tier_type == 2
    assert data.tier_type_name == "Common"
    assert data.equippable is True
    assert data.default_damage_type == 0
    assert data.ammo_type == 0

    data = await destiny_manifest.get(db=db, table=DestinyRecordDefinition, primary_key=dummy_gotten_record_id)
    assert data.description == "Trophies from conquest in the Crucible."
    assert data.name == "Gotten Record"
    assert data.for_title_gilding is False
    assert data.objective_hashes == [1192806779]
    assert data.score_value == 0
    assert data.parent_node_hashes == []

    data = await destiny_manifest.get(db=db, table=DestinyInventoryBucketDefinition, primary_key=1498876634)
    assert data.description == "Weapons that deal kinetic damage"
    assert data.name == "Kinetic Weapons"
    assert data.category == 3
    assert data.item_count == 10
    assert data.location == 1

    data = await destiny_manifest.get(db=db, table=DestinyPresentationNodeDefinition, primary_key=3790247699)
    assert data.description == ""
    assert data.name == "Items"
    assert data.objective_hash == 3395152237
    assert data.presentation_node_type == 1
    assert data.children_presentation_node_hash == [1068557105, 1528930164]
    assert data.children_collectible_hash == []
    assert data.children_record_hash == []
    assert data.children_metric_hash == []
    assert data.parent_node_hashes == []
    assert data.index == 0
    assert data.redacted is False

    data = await destiny_manifest.get(db=db, table=DestinySeasonPassDefinition, primary_key=155514181)
    assert data.name == "Season of the Undying"
    assert data.reward_progression_hash == 1628407317
    assert data.prestige_progression_hash == 3184735011
    assert data.index == 0

    data = await destiny_manifest.get(db=db, table=DestinyLoreDefinition, primary_key=dummy_lore_id)
    assert data.name == "The Gate Lord's Eye"
    assert (
        data.description
        == "An iris unfurls. Our gaze caught. Cortex clutched. Suspended.\n\nA million lights bend inward. Pulled on a wave of enigmatic tone.\n\nA million lights rip inward. Fall. Link. Scream. Cycle. Bleed. Blend. Cycle.\n\nOne light alone. Pulled. Discordant. Suspended in the Endless.\n\nScreams.\n\nAn iris unfurls.\n\nRun. Run. Run.\n\nAn iris unfurls.\n\nRun. Run.\n\nAn iris unfurls.\n\nRun.\n\nBlink. An iris folds in."
    )
    assert data.sub_title == "It looks through you, toward the infinite."
    assert data.redacted is False

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
    r = await client.post(f"/destiny/roles/{dummy_discord_guild_id}/create", json=orjson.loads(input_model2.json()))
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = RolesModel.parse_obj(r.json())
    assert len(data.roles) == 2

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

    input_model3 = copy.deepcopy(input_model)
    input_model3.role_id = 3
    input_model3.replaced_by_role_id = 2
    r = await client.post(f"/destiny/roles/{dummy_discord_guild_id}/create", json=orjson.loads(input_model3.json()))
    assert r.status_code == 200

    # deleting role 3 should not delete role 2
    r = await client.delete(f"/destiny/roles/{dummy_discord_guild_id}/delete/3")
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = RolesModel.parse_obj(r.json())
    assert len(data.roles) == 2
    for role in data.roles:
        assert role.role_id != 3

    # adding role 3 again
    r = await client.post(f"/destiny/roles/{dummy_discord_guild_id}/create", json=orjson.loads(input_model2.json()))
    assert r.status_code == 200

    # deleting role 1 should delete role 2
    r = await client.delete(f"/destiny/roles/{dummy_discord_guild_id}/delete/1")
    assert r.status_code == 200

    r = await client.get(f"/destiny/roles/{dummy_discord_guild_id}/get/all")
    assert r.status_code == 200
    data = RolesModel.parse_obj(r.json())
    assert len(data.roles) == 1
    for role in data.roles:
        assert role.role_id != 1
        assert role.role_id != 2

    # insert the og role again because we need it
    r = await client.post(f"/destiny/roles/{dummy_discord_guild_id}/create", json=orjson.loads(input_model.json()))
    assert r.status_code == 200

    assert cache.roles
    assert cache.guild_roles
