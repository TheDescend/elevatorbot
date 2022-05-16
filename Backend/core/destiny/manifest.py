import dataclasses

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud import destiny_manifest
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
)
from Backend.misc.cache import cache
from Backend.misc.helperFunctions import DefaultDict
from Backend.networking.bungieApi import BungieApi
from Backend.networking.bungieRoutes import manifest_route

default_bool = False
default_integer = -1
default_text = "Unknown"


@dataclasses.dataclass
class DestinyManifest:
    """Manifest specific API calls"""

    db: AsyncSession

    def __post_init__(self):
        # the network class
        self.api = BungieApi()

    async def update(self) -> bool:
        """Checks the local manifests versions and updates the local copy should it have changed"""

        # get the manifest
        db_manifest = destiny_manifest
        manifest = await self.api.get(route=manifest_route)

        # check if the downloaded version is different to ours in the db, if so drop entries and re-download info
        version = manifest.content["version"]
        db_version = await db_manifest.get_version(db=self.db)
        if db_version and (version == db_version.version):
            return False

        # version is different, so re-download
        path = manifest.content["jsonWorldComponentContentPaths"]["en"]

        # =============================================================================
        url = path["DestinyActivityTypeDefinition"]

        # delete old data
        await db_manifest.delete_definition(db=self.db, db_model=DestinyActivityTypeDefinition)

        # get new data and save values as defaultdict
        data = await self.api.get(f"https://www.bungie.net{url}")
        content = DefaultDict(data.content)

        # save data to bulk insert later
        to_insert = []
        for reference_id, values in content.items():
            to_insert.append(
                DestinyActivityTypeDefinition(
                    reference_id=int(reference_id),
                    description=values.get("displayProperties", "description", default=default_text),
                    name=values.get("displayProperties", "name", default=default_text),
                )
            )

        # insert data in table
        await db_manifest.insert_definition(db=self.db, db_model=DestinyActivityTypeDefinition, to_insert=to_insert)

        # =============================================================================
        url = path["DestinyActivityModeDefinition"]

        # delete old data
        await db_manifest.delete_definition(db=self.db, db_model=DestinyActivityModeDefinition)

        # get new data and save values as defaultdict
        data = await self.api.get(f"https://www.bungie.net{url}")
        content = DefaultDict(data.content)

        # save data to bulk insert later
        to_insert = []
        for reference_id, values in content.items():
            to_insert.append(
                DestinyActivityModeDefinition(
                    reference_id=int(reference_id),
                    parent_hashes=values.get("parentHashes", default=[]),
                    mode_type=values.get("modeType", default=default_integer),
                    description=values.get("displayProperties", "description", default=default_text),
                    name=values.get("displayProperties", "name", default=default_text),
                    activity_mode_category=values.get("activityModeCategory", default=default_integer),
                    is_team_based=values.get("isTeamBased", default=default_bool),
                    friendly_name=values.get("friendlyName", default=default_text),
                    display=values.get("display", default=default_bool),
                    redacted=values.get("redacted", default=default_bool),
                )
            )

        # insert data in table
        await db_manifest.insert_definition(db=self.db, db_model=DestinyActivityModeDefinition, to_insert=to_insert)

        # =============================================================================
        url = path["DestinyActivityDefinition"]

        # delete old data
        await db_manifest.delete_definition(db=self.db, db_model=DestinyActivityDefinition)

        # get new data and save values as defaultdict
        data = await self.api.get(f"https://www.bungie.net{url}")
        content = DefaultDict(data.content)

        # save data to bulk insert later
        to_insert = []
        for reference_id, values in content.items():
            activity_type_hash = values.get("activityTypeHash")

            # sometimes bungie is not including some fields which is very annoying
            # luckily we can get the info from somewhere else
            direct_activity_mode_hash = values.get("directActivityModeHash")
            direct_activity_mode_type = values.get("directActivityModeType")
            activity_mode_hashes = values.get("activityModeHashes")
            activity_mode_types = values.get("activityModeTypes")

            # fill out the data with the activityTypeHash field which is the key to *some* mode definitions
            if not direct_activity_mode_hash:
                data = await destiny_manifest.get(
                    db=self.db, table=DestinyActivityModeDefinition, primary_key=activity_type_hash
                )
                if not data:
                    # sometimes we get entries without a mode definition
                    # set the mode type to 0
                    direct_activity_mode_type = 0
                    activity_mode_types = []

                else:
                    direct_activity_mode_type = data.mode_type
                    activity_mode_types = [direct_activity_mode_type]

                direct_activity_mode_hash = activity_type_hash
                activity_mode_hashes = [activity_type_hash]

            pgcr_image_url = values.get("pgcrImage")
            to_insert.append(
                DestinyActivityDefinition(
                    reference_id=int(reference_id),
                    description=values.get("displayProperties", "description", default=default_text),
                    name=values.get("displayProperties", "name", default=default_text),
                    pgcr_image_url=f"https://www.bungie.net/{pgcr_image_url}" if pgcr_image_url else None,
                    activity_light_level=values.get("activityLightLevel", default=default_integer),
                    destination_hash=values.get("destinationHash", default=default_integer),
                    place_hash=values.get("placeHash", default=default_integer),
                    activity_type_hash=activity_type_hash,
                    is_pvp=values.get("isPvP", default=default_bool),
                    direct_activity_mode_hash=direct_activity_mode_hash,
                    direct_activity_mode_type=direct_activity_mode_type,
                    activity_mode_hashes=activity_mode_hashes,
                    activity_mode_types=activity_mode_types,
                    matchmade=values.get("matchmaking", "isMatchmade", default=default_bool),
                    max_players=values.get("matchmaking", "maxParty", default=0),
                )
            )

        # insert data in table
        await db_manifest.insert_definition(db=self.db, db_model=DestinyActivityDefinition, to_insert=to_insert)

        # =============================================================================
        url = path["DestinyCollectibleDefinition"]

        # delete old data
        await db_manifest.delete_definition(db=self.db, db_model=DestinyCollectibleDefinition)

        # get new data and save values as defaultdict
        data = await self.api.get(f"https://www.bungie.net{url}")
        content = DefaultDict(data.content)

        # save data to bulk insert later
        to_insert = []
        for reference_id, values in content.items():
            # hashes can be classified
            if (source_hash := values.get("sourceHash", default=default_integer)) == "Classified":
                source_hash = -1

            to_insert.append(
                DestinyCollectibleDefinition(
                    reference_id=int(reference_id),
                    description=values.get("displayProperties", "description", default=default_text),
                    name=values.get("displayProperties", "name", default=default_text),
                    source_hash=source_hash,
                    item_hash=values.get("itemHash", default=default_integer),
                    parent_node_hashes=values.get("parentNodeHashes", default=[]),
                )
            )

        # insert data in table
        await db_manifest.insert_definition(db=self.db, db_model=DestinyCollectibleDefinition, to_insert=to_insert)

        # =============================================================================
        url = path["DestinyInventoryItemDefinition"]

        # delete old data
        await db_manifest.delete_definition(db=self.db, db_model=DestinyInventoryItemDefinition)

        # get new data and save values as defaultdict
        data = await self.api.get(f"https://www.bungie.net{url}")
        content = DefaultDict(data.content)

        # save data to bulk insert later
        to_insert = []
        for reference_id, values in content.items():
            to_insert.append(
                DestinyInventoryItemDefinition(
                    reference_id=int(reference_id),
                    description=values.get("displayProperties", "description", default=default_text),
                    name=values.get("displayProperties", "name", default=default_text),
                    flavor_text=values.get("flavorText", default=default_text),
                    item_type=values.get("itemType", default=default_integer),
                    item_sub_type=values.get("itemSubType", default=default_integer),
                    class_type=values.get("classType", default=default_integer),
                    bucket_type_hash=values.get("inventory", "bucketTypeHash", default=default_integer),
                    tier_type=values.get("inventory", "tierType", default=default_integer),
                    tier_type_name=values.get("inventory", "tierTypeName", default=default_text),
                    equippable=values.get("equippable", default=default_bool),
                    default_damage_type=values.get("defaultDamageType", default=default_integer),
                    ammo_type=values.get("equippingBlock", "ammoType", default=0),
                )
            )

        # insert data in table
        await db_manifest.insert_definition(db=self.db, db_model=DestinyInventoryItemDefinition, to_insert=to_insert)

        # =============================================================================
        url = path["DestinyRecordDefinition"]

        # delete old data
        await db_manifest.delete_definition(db=self.db, db_model=DestinyRecordDefinition)

        # get new data and save values as defaultdict
        data = await self.api.get(f"https://www.bungie.net{url}")
        content = DefaultDict(data.content)

        # save data to bulk insert later
        to_insert = []
        for reference_id, values in content.items():
            to_insert.append(
                DestinyRecordDefinition(
                    reference_id=int(reference_id),
                    description=values.get("displayProperties", "description", default=default_text),
                    name=values.get("displayProperties", "name", default=default_text),
                    for_title_gilding=values.get("forTitleGilding", default=default_bool),
                    title_name=values.get("titleInfo", "titlesByGender", "Male", default=default_text),
                    objective_hashes=values.get("objectiveHashes", default=[]),
                    score_value=values.get("completionInfo", "ScoreValue", default=0),
                    parent_node_hashes=values.get("parentNodeHashes", default=[]),
                )
            )

        # insert data in table
        await db_manifest.insert_definition(db=self.db, db_model=DestinyRecordDefinition, to_insert=to_insert)

        # =============================================================================
        url = path["DestinyInventoryBucketDefinition"]

        # delete old data
        await db_manifest.delete_definition(db=self.db, db_model=DestinyInventoryBucketDefinition)

        # get new data and save values as defaultdict
        data = await self.api.get(f"https://www.bungie.net{url}")
        content = DefaultDict(data.content)

        # save data to bulk insert later
        to_insert = []
        for reference_id, values in content.items():
            to_insert.append(
                DestinyInventoryBucketDefinition(
                    reference_id=int(reference_id),
                    description=values.get("displayProperties", "description", default=default_text),
                    name=values.get("displayProperties", "name", default=default_text),
                    category=values.get("category", default=default_integer),
                    item_count=values.get("itemCount", default=default_integer),
                    location=values.get("location", default=default_integer),
                )
            )

        # insert data in table
        await db_manifest.insert_definition(db=self.db, db_model=DestinyInventoryBucketDefinition, to_insert=to_insert)

        # =============================================================================
        url = path["DestinyPresentationNodeDefinition"]

        # delete old data
        await db_manifest.delete_definition(db=self.db, db_model=DestinyPresentationNodeDefinition)

        # get new data and save values as defaultdict
        data = await self.api.get(f"https://www.bungie.net{url}")
        content = DefaultDict(data.content)

        # save data to bulk insert later
        to_insert = []
        for reference_id, values in content.items():
            to_insert.append(
                DestinyPresentationNodeDefinition(
                    reference_id=int(reference_id),
                    description=values.get("displayProperties", "description", default=default_text),
                    name=values.get("displayProperties", "name", default=default_text),
                    objective_hash=values.get("objectiveHash"),
                    presentation_node_type=values.get("presentationNodeType", default=default_integer),
                    children_presentation_node_hash=[
                        list(x.values())[0] for x in values.get("children", "presentationNodes", default=[])
                    ],
                    children_collectible_hash=[
                        list(x.values())[0] for x in values.get("children", "collectibles", default=[])
                    ],
                    children_record_hash=[list(x.values())[0] for x in values.get("children", "records", default=[])],
                    children_metric_hash=[list(x.values())[0] for x in values.get("children", "metrics", default=[])],
                    parent_node_hashes=values.get("parentNodeHashes", default=[]),
                    index=values.get("index", default=default_integer),
                    redacted=values.get("redacted", default=default_bool),
                    completion_record_hash=values.get("completionRecordHash"),
                )
            )

        # insert data in table
        await db_manifest.insert_definition(db=self.db, db_model=DestinyPresentationNodeDefinition, to_insert=to_insert)

        # =============================================================================
        url = path["DestinySeasonPassDefinition"]

        # delete old data
        await db_manifest.delete_definition(db=self.db, db_model=DestinySeasonPassDefinition)

        # get new data and save values as defaultdict
        data = await self.api.get(f"https://www.bungie.net{url}")
        content = DefaultDict(data.content)

        # save data to bulk insert later
        to_insert = []
        for reference_id, values in content.items():
            to_insert.append(
                DestinySeasonPassDefinition(
                    reference_id=int(reference_id),
                    name=values.get("displayProperties", "name", default=default_text),
                    reward_progression_hash=values.get("rewardProgressionHash", default=default_integer),
                    prestige_progression_hash=values.get("prestigeProgressionHash", default=default_integer),
                    index=values.get("index", default=default_integer),
                )
            )

        # insert data in table
        await db_manifest.insert_definition(db=self.db, db_model=DestinySeasonPassDefinition, to_insert=to_insert)

        # =============================================================================
        url = path["DestinyLoreDefinition"]

        # delete old data
        await db_manifest.delete_definition(db=self.db, db_model=DestinyLoreDefinition)

        # get new data and save values as defaultdict
        data = await self.api.get(f"https://www.bungie.net{url}")
        content = DefaultDict(data.content)

        # save data to bulk insert later
        to_insert = []
        for reference_id, values in content.items():
            to_insert.append(
                DestinyLoreDefinition(
                    reference_id=int(reference_id),
                    name=values.get("displayProperties", "name", default=default_text),
                    description=values.get("displayProperties", "description", default=default_text),
                    sub_title=values.get("subtitle"),
                    redacted=values.get("redacted", default=default_bool),
                )
            )

        # insert data in table
        await db_manifest.insert_definition(db=self.db, db_model=DestinyLoreDefinition, to_insert=to_insert)

        # invalidate caches
        cache.reset()

        # update version entry
        await db_manifest.upsert_version(db=self.db, version=version)

        return True
