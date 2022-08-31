import asyncio
import copy
from typing import Optional

from bungio.models import (
    MISSING,
    DestinyActivityDefinition,
    DestinyActivityModeDefinition,
    DestinyActivityModeType,
    DestinyCollectibleDefinition,
    DestinyInventoryItemDefinition,
    DestinyItemType,
    DestinyLoreDefinition,
    DestinyPresentationNodeDefinition,
    DestinyRecordDefinition,
    DestinySeasonPassDefinition,
)

from Backend.bungio.client import get_bungio_client
from Backend.core.errors import CustomException
from Backend.database.base import is_test_mode
from Shared.enums.destiny import DestinyPresentationNodesEnum
from Shared.networkingSchemas import (
    SeasonalChallengesModel,
    SeasonalChallengesRecordModel,
    SeasonalChallengesTopicsModel,
)
from Shared.networkingSchemas.destiny import DestinyActivityModel, DestinyLoreModel

get_challenging_solo_activities_lock = asyncio.Lock()
get_gm_lock = asyncio.Lock()
get_activities_lock = asyncio.Lock()
get_collectible_lock = asyncio.Lock()
get_triumph_lock = asyncio.Lock()
get_lore_lock = asyncio.Lock()
get_season_pass_lock = asyncio.Lock()
get_seasonal_challenges_definition_lock = asyncio.Lock()
get_catalyst_lock = asyncio.Lock()
get_item_lock = asyncio.Lock()
get_all_weapons_lock = asyncio.Lock()
get_seals_lock = asyncio.Lock()


class CRUDManifest:
    # Manifest Definitions. Saving DB calls since 1982. Make sure to `asyncio.Lock():` them
    _manifest_season_pass_definition: DestinySeasonPassDefinition = None
    _manifest_seasonal_challenges_definition: SeasonalChallengesModel = None

    # DestinyInventoryItemDefinition
    _manifest_items: dict[int, Optional[DestinyInventoryItemDefinition]] = {}
    _manifest_weapons: dict[int, DestinyInventoryItemDefinition] = {}

    # DestinyCollectibleDefinition
    _manifest_collectibles: dict[int, DestinyCollectibleDefinition] = {}

    # DestinyLoreModel
    _manifest_lore: dict[int, DestinyLoreModel] = {}

    # DestinyRecordDefinition
    _manifest_triumphs: dict[int, DestinyRecordDefinition] = {}
    _manifest_seals: dict[DestinyPresentationNodeDefinition, list[DestinyRecordDefinition]] = {}
    _manifest_catalysts: list[DestinyRecordDefinition] = []

    # DestinyActivityModel
    _manifest_activities: dict[int, DestinyActivityModel] = {}
    _manifest_grandmasters: list[DestinyActivityModel] = []
    _manifest_interesting_solos: dict[str, list[DestinyActivityModel]] = {}  # Key: activity_category

    async def reset(self):
        """Reset the caches after a manifest update"""

        self._manifest_weapons = {}
        await destiny_manifest.get_all_weapons()

        self._manifest_season_pass_definition = None  # noqa
        await destiny_manifest.get_current_season_pass()

        self._manifest_seasonal_challenges_definition = None  # noqa
        await self.get_seasonal_challenges_definition()

        self._manifest_items = {}
        # per item, so not populated here

        self._manifest_collectibles = {}
        await destiny_manifest.get_all_collectibles()

        self._manifest_triumphs = {}
        await destiny_manifest.get_all_triumphs()

        self._manifest_seals = {}
        await destiny_manifest.get_seals()

        self._manifest_lore = {}
        await destiny_manifest.get_all_lore()

        self._manifest_catalysts = []
        await destiny_manifest.get_catalysts()

        self._manifest_activities = {}
        await destiny_manifest.get_all_activities()

        self._manifest_grandmasters = []
        await destiny_manifest.get_grandmaster_nfs()

        self._manifest_interesting_solos = {}
        await destiny_manifest.get_challenging_solo_activities()

    async def get_all_weapons(self) -> dict[int, DestinyInventoryItemDefinition]:
        """Return all weapons"""

        async with get_all_weapons_lock:
            if not self._manifest_weapons:
                results: list[DestinyInventoryItemDefinition] = await get_bungio_client().manifest.fetch_all(
                    manifest_class=DestinyInventoryItemDefinition,
                    filter=f"""CAST(data ->> 'itemType' AS INTEGER) = {DestinyItemType.WEAPON.value}""",
                )
                for result in results:
                    self._manifest_weapons[result.hash] = result
                    self._manifest_items[result.hash] = result
        return self._manifest_weapons

    async def get_weapon(self, weapon_id: int) -> DestinyInventoryItemDefinition:
        """Gets weapon"""

        weapons = await self.get_all_weapons()
        if not (weapon := weapons.get(int(weapon_id))):
            raise CustomException("BungieDestinyItemNotExist")
        return weapon

    async def get_seasonal_challenges_definition(self) -> SeasonalChallengesModel:
        """Gets all seasonal challenges"""

        async with get_seasonal_challenges_definition_lock:
            if not self._manifest_seasonal_challenges_definition:
                definition = SeasonalChallengesModel()

                # get the info from the db
                sc_presentation_node: DestinyPresentationNodeDefinition = await get_bungio_client().manifest.fetch(
                    manifest_class=DestinyPresentationNodeDefinition, value="3443694067"
                )

                # loop through those categories and get the "Weekly" one
                for category in sc_presentation_node.children.presentation_nodes:
                    await category.fetch_manifest_information(include=["manifest_presentation_node_hash"])
                    category = category.manifest_presentation_node_hash
                    if category.display_properties.name == "Weekly":
                        # loop through the seasonal challenges topics (Week1, Week2, etc...)
                        for sc_topic in category.children.presentation_nodes:
                            await sc_topic.fetch_manifest_information(include=["manifest_presentation_node_hash"])
                            sc_topic = sc_topic.manifest_presentation_node_hash

                            # loop through the actual seasonal challenges
                            topic = SeasonalChallengesTopicsModel(name=sc_topic.display_properties.name)
                            for sc_record in sc_topic.children.records:
                                await sc_record.fetch_manifest_information(include=["manifest_record_hash"])
                                sc = sc_record.manifest_record_hash

                                topic.seasonal_challenges.append(
                                    SeasonalChallengesRecordModel(
                                        record_id=sc.hash,
                                        name=sc.display_properties.name,
                                        description=sc.display_properties.description,
                                    )
                                )

                            definition.topics.append(topic)
                        break

                self._manifest_seasonal_challenges_definition = definition

        return self._manifest_seasonal_challenges_definition

    async def get_item(self, item_id: int) -> Optional[DestinyInventoryItemDefinition]:
        """Return the item"""

        async with get_item_lock:
            if item_id not in self._manifest_items:
                item: DestinyInventoryItemDefinition = await get_bungio_client().manifest.fetch(
                    manifest_class=DestinyInventoryItemDefinition, value=str(item_id)
                )
                self._manifest_items.update({item_id: item})

        return self._manifest_items[item_id]

    async def get_activity_mode(
        self, activity: DestinyActivityDefinition
    ) -> tuple[DestinyActivityModeType, list[DestinyActivityModeType]]:
        """Get the mode of an activity"""

        # sometimes bungie is not including some fields which is very annoying
        # luckily we can get the info from somewhere else
        if activity.direct_activity_mode_type is not MISSING and activity.activity_mode_types is not MISSING:
            return DestinyActivityModeType(activity.direct_activity_mode_type), activity.activity_mode_types

        # fill out the data with the activityTypeHash field which is the key to *some* mode definitions
        result: DestinyActivityModeDefinition = await get_bungio_client().manifest.fetch(
            manifest_class=DestinyActivityModeDefinition, value=activity.activity_type_hash
        )
        if result:
            mode_type = result.mode_type
        else:
            mode_type = DestinyActivityModeType.NONE
        return mode_type, [mode_type]

    async def get_all_activities(self) -> dict[int, DestinyActivityModel]:
        """Gets all activities"""

        async with get_activities_lock:
            if not self._manifest_activities:
                results: list[DestinyActivityDefinition] = await get_bungio_client().manifest.fetch_all(
                    manifest_class=DestinyActivityDefinition
                )

                # loop through all activities and save them by name
                data: dict[str, list[DestinyActivityDefinition]] = {}
                for activity in results:
                    name = activity.display_properties.name
                    if name not in data:
                        data.update({name: []})
                    data[name].append(activity)

                # format them correctly
                result = {}
                for activities in data.values():
                    model = DestinyActivityModel(
                        name=activities[0].display_properties.name or "Unknown",
                        description=activities[0].display_properties.description,
                        matchmade=activities[0].matchmaking.is_matchmade if activities[0].matchmaking else False,
                        max_players=activities[0].matchmaking.max_players if activities[0].matchmaking else False,
                        activity_ids=[activity.hash for activity in activities],
                        mode=(await self.get_activity_mode(activities[0]))[0].value,
                        image_url=f"https://www.bungie.net/{activities[0].pgcr_image}"
                        if activities[0].pgcr_image
                        else None,
                    )
                    for reference_id in model.activity_ids:
                        result[reference_id] = model

                self._manifest_activities = {k: v for k, v in sorted(result.items(), key=lambda item: item[1].name)}

        return self._manifest_activities

    async def get_activity(self, activity_id: int) -> DestinyActivityModel:
        """Gets activity"""

        activities = await self.get_all_activities()
        if not (activity := activities.get(int(activity_id))):
            raise CustomException("BungieDestinyItemNotExist")
        return activity

    async def get_all_collectibles(self) -> dict[int, DestinyCollectibleDefinition]:
        """Gets all collectibles"""

        async with get_collectible_lock:
            if not self._manifest_collectibles:
                results: list[DestinyCollectibleDefinition] = await get_bungio_client().manifest.fetch_all(
                    manifest_class=DestinyCollectibleDefinition
                )
                self._manifest_collectibles = {result.hash: result for result in results}
        return self._manifest_collectibles

    async def get_all_triumphs(self) -> dict[int, DestinyRecordDefinition]:
        """Gets all triumphs"""

        async with get_triumph_lock:
            if not self._manifest_triumphs:
                results: list[DestinyRecordDefinition] = await get_bungio_client().manifest.fetch_all(
                    manifest_class=DestinyRecordDefinition
                )
                self._manifest_triumphs = {result.hash: result for result in results}
        return self._manifest_triumphs

    async def get_triumph(self, triumph_id: int) -> DestinyRecordDefinition:
        """Gets triumph"""

        triumphs = await self.get_all_triumphs()
        if not (triumph := triumphs.get(int(triumph_id))):
            raise CustomException("BungieDestinyItemNotExist")
        return triumph

    async def get_seals(self) -> dict[DestinyPresentationNodeDefinition, list[DestinyRecordDefinition]]:
        """Returns a list of the current seals. Returns {title_name: DestinyRecordDefinition}"""

        async with get_seals_lock:
            if not self._manifest_seals:
                presentation_nodes: list[
                    DestinyPresentationNodeDefinition
                ] = await get_bungio_client().manifest.fetch_all(manifest_class=DestinyPresentationNodeDefinition)

                seals = []
                for node in presentation_nodes:
                    if DestinyPresentationNodesEnum.SEALS.value in node.parent_node_hashes:
                        seals.append(node)

                # now loop through all the seals and get the record infos
                for seal in seals:
                    records = []
                    for triumph in seal.children.records:
                        records.append(await self.get_triumph(triumph_id=triumph.record_hash))

                    self._manifest_seals[seal] = records

        return self._manifest_seals

    async def get_catalysts(self) -> list[DestinyRecordDefinition]:
        """Returns a list of the current catalysts"""

        async with get_catalyst_lock:
            if not self._manifest_catalysts:
                triumphs = await self.get_all_triumphs()

                for triumph in triumphs.values():
                    if " Catalyst" in triumph.display_properties.name:
                        self._manifest_catalysts.append(triumph)

        return self._manifest_catalysts

    async def get_all_lore(self) -> dict[int, DestinyLoreModel]:
        """Gets all lore"""

        # get them all from the db
        async with get_lore_lock:
            if not self._manifest_lore:
                results: list[DestinyLoreDefinition] = await get_bungio_client().manifest.fetch_all(
                    manifest_class=DestinyLoreDefinition
                )
                for result in results:
                    self._manifest_lore[result.hash] = DestinyLoreModel(
                        reference_id=result.hash,
                        name=result.display_properties.name,
                        description=result.display_properties.description,
                        sub_title=result.subtitle or None,
                        redacted=result.redacted,
                    )
        return self._manifest_lore

    async def get_current_season_pass(self) -> DestinySeasonPassDefinition:
        """Get the current season pass from the DB"""

        async with get_season_pass_lock:
            if not self._manifest_season_pass_definition:
                results: list[DestinySeasonPassDefinition] = await get_bungio_client().manifest.fetch_all(
                    manifest_class=DestinySeasonPassDefinition
                )
                self._manifest_season_pass_definition = results[-1]
        return self._manifest_season_pass_definition

    async def get_grandmaster_nfs(self) -> list[DestinyActivityModel]:
        """Get all grandmaster nfs"""

        async with get_gm_lock:
            if not self._manifest_grandmasters:
                results: list[DestinyActivityDefinition] = await get_bungio_client().manifest.fetch_all(
                    manifest_class=DestinyActivityDefinition
                )

                # loop through all activities and save the gms
                gms: dict[str, list[DestinyActivityDefinition]] = {}
                for result in results:
                    mode, modes = await self.get_activity_mode(result)

                    if DestinyActivityModeType.SCORED_NIGHTFALL in modes:
                        if "Grandmaster" in result.display_properties.name or result.activity_light_level == 1100:
                            if result.display_properties.description not in gms:
                                gms[result.display_properties.description] = []
                            gms[result.display_properties.description].append(result)

                # contains all gm ids
                all_grandmaster = DestinyActivityModel(
                    name="Grandmaster: All",
                    description="Grandmaster: All",
                    matchmade=False,
                    max_players=3,
                    activity_ids=[],
                )

                # format them correctly
                result = []
                for activities in gms.values():
                    reference_ids = [activity.hash for activity in activities]
                    all_grandmaster.activity_ids.extend(reference_ids)
                    result.append(
                        DestinyActivityModel(
                            name=f"Grandmaster: {activities[0].display_properties.description}",
                            description=f"Grandmaster: {activities[0].display_properties.description}",
                            matchmade=activities[0].matchmaking.is_matchmade,
                            max_players=activities[0].matchmaking.max_players,
                            activity_ids=reference_ids,
                            mode=activities[0].direct_activity_mode_type,
                            image_url=f"https://www.bungie.net/{activities[0].pgcr_image}"
                            if activities[0].pgcr_image
                            else None,
                        )
                    )

                result.insert(0, all_grandmaster)

                self._manifest_grandmasters = result
        return self._manifest_grandmasters

    async def get_challenging_solo_activities(self) -> dict[str, list[DestinyActivityModel]]:
        """Get activities that are difficult to solo"""

        async with get_challenging_solo_activities_lock:
            # check self
            if not self._manifest_interesting_solos:
                # key is the topic, then the activity display name
                # the value is a list with list[0] being what string the activity name has to include list[1] and what to exclude
                interesting_solos = {
                    "Dungeons": {
                        "Shattered Throne": ["Shattered Throne", None],
                        "Pit of Heresy": ["Pit of Heresy", None],
                        "Prophecy": ["Prophecy", None],
                        "Grasp of Avarice: Normal": ["Grasp of Avarice: Normal", None],
                        "Grasp of Avarice: Master": ["Grasp of Avarice: Master", None],
                        "Duality: Normal": ["Duality: Normal", None],
                        "Duality: Master": ["Duality: Master", None],
                    },
                    "Raids": {
                        "Eater of Worlds": ["Eater of Worlds", None],
                        "Last Wish": ["Last Wish", None],
                        "Vault of Glass": ["Vault of Glass", None],
                    },
                    "Story Missions": {
                        "The Whisper: Normal": ["The Whisper", "Heroic"],
                        "The Whisper: Master": ["The Whisper (Heroic)", None],
                        "Zero Hour: Normal": ["Zero Hour", "Heroic"],
                        "Zero Hour: Master": ["Zero Hour (Heroic)", None],
                        "Harbinger": ["Harbinger", None],
                        "Presage: Normal": ["Presage: Normal", None],
                        "Presage: Master": ["Presage: Master", None],
                    },
                    "Miscellaneous": {"Grandmaster Nightfalls": "grandmaster_nf"},
                }

                db_activities: list[DestinyActivityDefinition] = await get_bungio_client().manifest.fetch_all(
                    manifest_class=DestinyActivityDefinition
                )

                # loop through each of the entries
                for category, items in interesting_solos.items():
                    if category not in self._manifest_interesting_solos:
                        self._manifest_interesting_solos[category] = []

                    for activity_name, search_data in items.items():
                        # special handling for grandmasters
                        if search_data == "grandmaster_nf":
                            gms = await self.get_grandmaster_nfs()
                            gms = copy.deepcopy(gms)

                            # all gms is the first index there
                            data = gms[0]
                            data.name = activity_name

                        else:
                            # very inefficient, but it is a one-off
                            db_result = []
                            for entry in db_activities:
                                if search_data[0] in entry.display_properties.name:
                                    # do we want to exclude a search string
                                    if search_data[1] and search_data[1] in entry.display_properties.name:
                                        continue
                                    db_result.append(entry)

                            # loop through all activities and save them by name
                            data = None
                            for activity in db_result:
                                if not data:
                                    data = DestinyActivityModel(
                                        name=activity_name,
                                        description=activity.display_properties.description,
                                        matchmade=activity.matchmaking.is_matchmade,
                                        max_players=activity.matchmaking.max_players,
                                        activity_ids=[activity.hash],
                                        mode=(await self.get_activity_mode(activity))[0].value,
                                        image_url=f"https://www.bungie.net/{activity.pgcr_image}"
                                        if activity.pgcr_image
                                        else None,
                                    )
                                else:
                                    data.activity_ids.append(activity.hash)

                        # check that we got some
                        if not is_test_mode():
                            assert data is not None

                        if data:
                            self._manifest_interesting_solos[category].append(data)

        return self._manifest_interesting_solos


destiny_manifest = CRUDManifest()
