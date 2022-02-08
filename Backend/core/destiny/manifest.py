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
from Backend.networking.elevatorApi import ElevatorApi


@dataclasses.dataclass
class DestinyManifest:
    """Manifest specific API calls"""

    db: AsyncSession

    def __post_init__(self):
        # the network class
        self.api = BungieApi(
            db=self.db, i_understand_what_im_doing_and_that_setting_this_to_true_might_break_stuff=True
        )

    async def update(self, post_elevator: bool = True):
        """Checks the local manifests versions and updates the local copy should it have changed"""

        # get the manifest
        db_manifest = destiny_manifest
        manifest = await self.api.get(route=manifest_route)

        # check if the downloaded version is different to ours in the db, if so drop entries and re-download info
        version = manifest.content["version"]
        db_version = await db_manifest.get_version(db=self.db)
        if db_version and (version == db_version.version):
            return

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
                    description=values.get("displayProperties", "description"),
                    name=values.get("displayProperties", "name"),
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
                    parent_hashes=values.get("parentHashes"),
                    mode_type=values.get("modeType"),
                    description=values.get("displayProperties", "description"),
                    name=values.get("displayProperties", "name"),
                    activity_mode_category=values.get("activityModeCategory"),
                    is_team_based=values.get("isTeamBased"),
                    friendly_name=values.get("friendlyName"),
                    display=values.get("display"),
                    redacted=values.get("redacted"),
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
                    description=values.get("displayProperties", "description"),
                    name=values.get("displayProperties", "name"),
                    pgcr_image_url=f"https://www.bungie.net/{pgcr_image_url}" if pgcr_image_url else None,
                    activity_light_level=values.get("activityLightLevel"),
                    destination_hash=values.get("destinationHash"),
                    place_hash=values.get("placeHash"),
                    activity_type_hash=activity_type_hash,
                    is_pvp=values.get("isPvP"),
                    direct_activity_mode_hash=direct_activity_mode_hash,
                    direct_activity_mode_type=direct_activity_mode_type,
                    activity_mode_hashes=activity_mode_hashes,
                    activity_mode_types=activity_mode_types,
                    matchmade=values.get("matchmaking", "isMatchmade") or False,
                    max_players=values.get("matchmaking", "maxParty") or 0,
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
            to_insert.append(
                DestinyCollectibleDefinition(
                    reference_id=int(reference_id),
                    description=values.get("displayProperties", "description"),
                    name=values.get("displayProperties", "name"),
                    source_hash=values.get("sourceHash"),
                    item_hash=values.get("itemHash"),
                    parent_node_hashes=values.get("parentNodeHashes"),
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
                    description=values.get("displayProperties", "description"),
                    name=values.get("displayProperties", "name"),
                    flavor_text=values.get("flavorText"),
                    item_type=values.get("itemType"),
                    item_sub_type=values.get("itemSubType"),
                    class_type=values.get("classType"),
                    bucket_type_hash=values.get("inventory", "bucketTypeHash"),
                    tier_type=values.get("inventory", "tierType"),
                    tier_type_name=values.get("inventory", "tierTypeName") or "Unknown",
                    equippable=values.get("equippable"),
                    default_damage_type=values.get("defaultDamageType"),
                    ammo_type=values.get("equippingBlock", "ammoType"),
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
                    description=values.get("displayProperties", "description"),
                    name=values.get("displayProperties", "name"),
                    for_title_gilding=values.get("forTitleGilding"),
                    title_name=values.get("titleInfo", "titlesByGender", "Male"),
                    objective_hashes=values.get("objectiveHashes"),
                    score_value=values.get("completionInfo", "ScoreValue"),
                    parent_node_hashes=values.get("parentNodeHashes"),
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
                    description=values.get("displayProperties", "description"),
                    name=values.get("displayProperties", "name"),
                    category=values.get("category"),
                    item_count=values.get("itemCount"),
                    location=values.get("location"),
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
                    description=values.get("displayProperties", "description"),
                    name=values.get("displayProperties", "name"),
                    objective_hash=values.get("objectiveHash"),
                    presentation_node_type=values.get("presentationNodeType"),
                    children_presentation_node_hash=[
                        list(x.values())[0] for x in values.get("children", "presentationNodes")
                    ],
                    children_collectible_hash=[list(x.values())[0] for x in values.get("children", "collectibles")],
                    children_record_hash=[list(x.values())[0] for x in values.get("children", "records")],
                    children_metric_hash=[list(x.values())[0] for x in values.get("children", "metrics")],
                    parent_node_hashes=values.get("parentNodeHashes"),
                    index=values.get("index"),
                    redacted=values.get("redacted"),
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
                    name=values.get("displayProperties", "name"),
                    reward_progression_hash=values.get("rewardProgressionHash"),
                    prestige_progression_hash=values.get("prestigeProgressionHash"),
                    index=values.get("index"),
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
                    name=values.get("displayProperties", "name"),
                    description=values.get("displayProperties", "description"),
                    sub_title=values.get("subtitle"),
                    redacted=values.get("redacted"),
                )
            )

        # insert data in table
        await db_manifest.insert_definition(db=self.db, db_model=DestinyLoreDefinition, to_insert=to_insert)

        # invalidate caches
        cache.reset()

        # update version entry
        await db_manifest.upsert_version(db=self.db, version=version)

        if post_elevator:
            # populate the autocomplete options again
            elevator_api = ElevatorApi()
            await elevator_api.post(route_addition="/manifest_update")
