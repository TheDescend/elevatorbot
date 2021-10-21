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
    DestinyPresentationNodeDefinition,
    DestinyRecordDefinition,
)
from Backend.misc.helperFunctions import defaultdictify
from Backend.networking.bungieApi import BungieApi
from Backend.networking.BungieRoutes import manifest_route


@dataclasses.dataclass
class DestinyManifest:
    """Manifest specific API calls"""

    db: AsyncSession

    def __post_init__(self):
        # the network class
        self.api = BungieApi(
            db=self.db, i_understand_what_im_doing_and_that_setting_this_to_true_might_break_stuff=True
        )

    async def update(self):
        """Checks the local manifests versions and updates the local copy should it have changed"""

        # _get the manifest
        db_manifest = destiny_manifest
        manifest = await self.api.get(route=manifest_route)

        # check if the downloaded version is different to ours in the db, if so drop entries and re-download info
        version = manifest.content["version"]
        if version == await db_manifest.get_version(db=self.db):
            return

        # version is different, so re-download
        for definition_name, url in manifest.content["jsonWorldComponentContentPaths"]["en"].items():
            match definition_name:
                case "DestinyActivityDefinition":
                    # delete old data
                    await db_manifest.delete_definition(db=self.db, db_model=DestinyActivityDefinition)

                    # _get new data and save values as defaultdict
                    data = await self.api.get(f"https://www.bungie.net{url}")
                    content = defaultdictify(data.content)

                    # save data to bulk insert later
                    to_insert = []
                    for reference_id, values in content.items():
                        to_insert.append(
                            DestinyActivityDefinition(
                                reference_id=int(reference_id),
                                description=values["displayProperties"]["description"],
                                name=values["displayProperties"]["name"],
                                activity_level=values["activityLevel"] if "activityLevel" in values else 0,
                                activity_light_level=values["activityLightLevel"],
                                destination_hash=values["destinationHash"],
                                place_hash=values["placeHash"],
                                activity_type_hash=values["activityTypeHash"],
                                is_pvp=values["isPvP"],
                                direct_activity_mode_hash=values["directActivityModeHash"],
                                direct_activity_mode_type=values["directActivityModeType"],
                                activity_mode_hashes=values["activityModeHashes"],
                                activity_mode_types=values["activityModeTypes"],
                             )
                        )

                    # insert data in table
                    await db_manifest.insert_definition(db=self.db, db_model=DestinyActivityDefinition, to_insert=to_insert)

                case "DestinyActivityTypeDefinition":
                    # delete old data
                    await db_manifest.delete_definition(db=self.db, db_model=DestinyActivityTypeDefinition)

                    # _get new data and save values as defaultdict
                    data = await self.api.get(f"https://www.bungie.net{url}")
                    content = defaultdictify(data.content)

                    # save data to bulk insert later
                    to_insert = []
                    for reference_id, values in content.items():
                        to_insert.append(
                            DestinyActivityTypeDefinition(
                                reference_id=int(reference_id),
                                description=values["displayProperties"]["description"],
                                name=values["displayProperties"]["name"],
                            )
                        )

                    # insert data in table
                    await db_manifest.insert_definition(db=self.db, db_model=DestinyActivityTypeDefinition, to_insert=to_insert)

                case "DestinyActivityModeDefinition":
                    # delete old data
                    await db_manifest.delete_definition(db=self.db, db_model=DestinyActivityModeDefinition)

                    # _get new data and save values as defaultdict
                    data = await self.api.get(f"https://www.bungie.net{url}")
                    content = defaultdictify(data.content)

                    # save data to bulk insert later
                    to_insert = []
                    for reference_id, values in content.items():
                        to_insert.append(
                            DestinyActivityModeDefinition(
                                reference_id=int(reference_id),
                                parent_hashes=values["parentHashes"],
                                mode_type=values["modeType"],
                                description=values["displayProperties"]["description"],
                                name=values["displayProperties"]["name"],
                                activity_mode_category=values["activityModeCategory"],
                                is_team_based=values["isTeamBased"],
                                friendly_name=values["friendlyName"],
                                display=values["display"],
                                redacted=values["redacted"],
                            )
                        )

                    # insert data in table
                    await db_manifest.insert_definition(db=self.db, db_model=DestinyActivityModeDefinition, to_insert=to_insert)

                case "DestinyCollectibleDefinition":
                    # delete old data
                    await db_manifest.delete_definition(db=self.db, db_model=DestinyCollectibleDefinition)

                    # _get new data and save values as defaultdict
                    data = await self.api.get(f"https://www.bungie.net{url}")
                    content = defaultdictify(data.content)

                    # save data to bulk insert later
                    to_insert = []
                    for reference_id, values in content.items():
                        to_insert.append(
                            DestinyCollectibleDefinition(
                                reference_id=int(reference_id),
                                description=values["displayProperties"]["description"],
                                name=values["displayProperties"]["name"],
                                source_hash=values["sourceHash"],
                                item_hash=values["itemHash"],
                                parent_node_hashes=values["parentNodeHashes"],
                            )
                        )

                    # insert data in table
                    await db_manifest.insert_definition(db=self.db, db_model=DestinyCollectibleDefinition, to_insert=to_insert)

                case "DestinyInventoryItemDefinition":
                    # delete old data
                    await db_manifest.delete_definition(db=self.db, db_model=DestinyInventoryItemDefinition)

                    # _get new data and save values as defaultdict
                    data = await self.api.get(f"https://www.bungie.net{url}")
                    content = defaultdictify(data.content)

                    # save data to bulk insert later
                    to_insert = []
                    for reference_id, values in content.items():
                        to_insert.append(
                            DestinyInventoryItemDefinition(
                                reference_id=int(reference_id),
                                description=values["displayProperties"]["description"],
                                name=values["displayProperties"]["name"],
                                class_type=values["classType"],
                                bucket_type_hash=values["inventory"]["bucketTypeHash"],
                                tier_type_hash=values["inventory"]["tierTypeHash"],
                                tier_type_name=values["inventory"]["tierTypeName"],
                                equippable=values["equippable"],
                            )
                        )

                    # insert data in table
                    await db_manifest.insert_definition(db=self.db, db_model=DestinyInventoryItemDefinition, to_insert=to_insert)

                case "DestinyRecordDefinition":
                    # delete old data
                    await db_manifest.delete_definition(db=self.db, db_model=DestinyRecordDefinition)

                    # _get new data and save values as defaultdict
                    data = await self.api.get(f"https://www.bungie.net{url}")
                    content = defaultdictify(data.content)

                    # save data to bulk insert later
                    to_insert = []
                    for reference_id, values in content.items():
                        to_insert.append(
                            DestinyRecordDefinition(
                                reference_id=int(reference_id),
                                description=values["displayProperties"]["description"],
                                name=values["displayProperties"]["name"],
                                has_title=values["titleInfo"]["hasTitle"],
                                title_name=values["titleInfo"]["titlesByGender"]["Male"],
                                objective_hashes=values["objectiveHashes"],
                                score_value=values["completionInfo"]["ScoreValue"],
                                parent_node_hashes=values["parentNodeHashes"],
                            )
                        )

                    # insert data in table
                    await db_manifest.insert_definition(db=self.db, db_model=DestinyRecordDefinition, to_insert=to_insert)

                case "DestinyInventoryBucketDefinition":
                    # delete old data
                    await db_manifest.delete_definition(db=self.db, db_model=DestinyInventoryBucketDefinition)

                    # _get new data and save values as defaultdict
                    data = await self.api.get(f"https://www.bungie.net{url}")
                    content = defaultdictify(data.content)

                    # save data to bulk insert later
                    to_insert = []
                    for reference_id, values in content.items():
                        to_insert.append(
                            DestinyInventoryBucketDefinition(
                                reference_id=int(reference_id),
                                description=values["displayProperties"]["description"],
                                name=values["displayProperties"]["name"],
                                category=values["category"],
                                item_count=values["itemCount"],
                                location=values["location"],
                            )
                        )

                    # insert data in table
                    await db_manifest.insert_definition(db=self.db, db_model=DestinyInventoryBucketDefinition, to_insert=to_insert)

                case "DestinyPresentationNodeDefinition":
                    # delete old data
                    await db_manifest.delete_definition(db=self.db, db_model=DestinyPresentationNodeDefinition)

                    # _get new data and save values as defaultdict
                    data = await self.api.get(f"https://www.bungie.net{url}")
                    content = defaultdictify(data.content)

                    # save data to bulk insert later
                    to_insert = []
                    for reference_id, values in content.items():
                        to_insert.append(
                            DestinyPresentationNodeDefinition(
                                reference_id=int(reference_id),
                                description=values["displayProperties"]["description"],
                                name=values["displayProperties"]["name"],
                                objective_hash=values["objectiveHash"],
                                presentation_node_type=values["presentationNodeType"],
                                children_presentation_node_hash=[list(x.values())[0] for x in values["children"]["presentationNodes"]],
                                children_collectible_hash=[list(x.values())[0] for x in values["children"]["collectibles"]],
                                children_record_hash=[list(x.values())[0] for x in values["children"]["records"]],
                                children_metric_hash=[list(x.values())[0] for x in values["children"]["metrics"]],
                                parent_node_hashes=values["parentNodeHashes"],
                                index=values["index"],
                                redacted=values["redacted"],
                            )
                        )

                    # insert data in table
                    await db_manifest.insert_definition(db=self.db, db_model=DestinyPresentationNodeDefinition, to_insert=to_insert)

        # update version entry
        await db_manifest.upsert_version(db=self.db, version=version)
