import asyncio
import copy
import dataclasses
import datetime
from contextlib import AsyncExitStack
from typing import Literal, Optional

from anyio import to_thread
from bungio.models import (
    DestinyClass,
    DestinyCollectibleComponent,
    DestinyCollectibleState,
    DestinyCraftableComponent,
    DestinyHistoricalStatsAccountResult,
    DestinyItemComponent,
    DestinyMetricComponent,
    DestinyProfileResponse,
    DestinyRecordComponent,
    DestinyRecordState,
    DestinyStatsGroupType,
    GroupsForMemberFilter,
    GroupType,
)
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.bungio.manifest import destiny_manifest
from Backend.core.errors import CustomException
from Backend.crud import crud_activities, discord_users
from Backend.crud.destiny.collectibles import collectibles
from Backend.crud.destiny.records import records
from Backend.database import acquire_db_session
from Backend.database.models import Collectibles, DiscordUsers, Records
from Backend.misc.cache import cache
from Shared.enums.destiny import DestinyInventoryBucketEnum, DestinyPresentationNodeWeaponSlotEnum
from Shared.functions.formatting import make_progress_bar_text
from Shared.functions.helperFunctions import get_now_with_tz
from Shared.networkingSchemas import DestinyAllMaterialsModel, DestinyNamedValueItemModel, ValueModel
from Shared.networkingSchemas.destiny import (
    BoolModelObjective,
    BoolModelRecord,
    DestinyCatalystModel,
    DestinyCatalystsModel,
    DestinyCharacterModel,
    DestinyCharactersModel,
    DestinyRecordModel,
    DestinySealModel,
    DestinySealsModel,
    DestinyTriumphScoreModel,
    SeasonalChallengesModel,
)
from Shared.networkingSchemas.destiny.clan import DestinyClanModel

has_triumph_lock = asyncio.Lock()
has_collectible_lock = asyncio.Lock()
get_season_pass_level_lock = asyncio.Lock()
get_seasonal_challenges_lock = asyncio.Lock()


@dataclasses.dataclass
class DestinyProfile:
    """User specific API calls"""

    db: AsyncSession
    user: DiscordUsers

    _triumphs: dict[int | str, DestinyRecordComponent | int] = dataclasses.field(
        init=False, default_factory=dict, repr=False
    )
    _collectibles: dict[int, DestinyCollectibleComponent] = dataclasses.field(
        init=False, default_factory=dict, repr=False
    )
    _profile: DestinyProfileResponse = dataclasses.field(init=False, default=None, repr=False)
    _inventory_bucket: dict[
        DestinyInventoryBucketEnum,
        dict[int, dict[Literal["item", "power_level", "quantity"], DestinyItemComponent | int]],
    ] = dataclasses.field(init=False, default_factory=dict, repr=False)

    def __post_init__(self):
        # some shortcuts
        self.discord_id = self.user.discord_id
        self.destiny_id = self.user.destiny_id
        self.system = self.user.system

    async def get_clan(self) -> DestinyClanModel:
        """Return the user's clan"""

        result = await self.user.bungio_user.get_groups_for_member(
            filter=GroupsForMemberFilter.ALL, group_type=GroupType.CLAN, auth=self.user.auth
        )

        if not result.results:
            raise CustomException("UserNoClan")
        return DestinyClanModel(id=result.results[0].group.group_id, name=result.results[0].group.name)

    async def get_seal_completion(self) -> DestinySealsModel:
        """Gets all seals and the users completion status"""

        # get the seals
        seals = await destiny_manifest.get_seals()

        # loop through the seals and format the data
        result = DestinySealsModel()
        for seal, triumphs in seals.items():
            # get user completion
            user_guilded_completed = []
            user_guilded_completed_int = 0
            user_completed = []
            user_completed_int = 0
            for triumph in triumphs:
                user_data = await self.has_triumph(triumph.hash)
                model = DestinyRecordModel(
                    name=triumph.display_properties.name,
                    description=triumph.display_properties.description,
                    completed=user_data.bool,
                )

                # handle guilded triumphs differently
                if triumph.for_title_gilding:
                    user_guilded_completed.append(model)
                    if user_data.bool:
                        user_guilded_completed_int += 1

                else:
                    user_completed.append(model)
                    if user_data.bool:
                        user_completed_int += 1

            # normal triumph data
            completion_percentage = user_completed_int / len(user_completed)

            # check if the seals maybe requires not all triumphs
            completion_triumph_id = seal.completion_record_hash
            if completion_triumph_id:
                if await self.has_triumph(completion_triumph_id):
                    completion_percentage = 1

            data = DestinySealModel(
                name=seal.display_properties.name,
                description=seal.display_properties.description,
                completed=True if completion_percentage == 1 else False,
                completion_percentage=completion_percentage,
                completion_status=make_progress_bar_text(completion_percentage),
                records=user_completed,
            )

            # add it to the correct type
            if data.completed:
                result.completed.append(data)
            else:
                result.not_completed.append(data)

            # guilded triumph data
            if user_guilded_completed:
                completion_percentage = user_guilded_completed_int / len(user_guilded_completed)
                data = DestinySealModel(
                    name=seal.display_properties.name,
                    description=seal.display_properties.description,
                    completed=True if completion_percentage == 1 else False,
                    completion_percentage=completion_percentage,
                    completion_status=make_progress_bar_text(completion_percentage),
                    records=user_guilded_completed,
                )

                # add it to the correct type
                if data.completed:
                    result.guilded.append(data)
                else:
                    result.not_guilded.append(data)

        return result

    async def get_catalyst_completion(self) -> DestinyCatalystsModel:
        """Gets all catalysts and the users completion status"""

        catalysts = await destiny_manifest.get_catalysts()
        triumphs = await self.get_triumphs()

        # check their completion
        result = DestinyCatalystsModel()
        for catalyst in catalysts:
            # get the completion rate
            if await self.has_triumph(catalyst.hash):
                completion_percentage = 1
            else:
                user_data = triumphs[catalyst.hash]

                if user_data.objectives and user_data.objectives[0].completion_value:
                    i = 0
                    percentages = []
                    for part in user_data.objectives:
                        i += 1
                        percentages.append(part.progress / part.completion_value if part.completion_value != 0 else 0)
                    completion_percentage = sum(percentages) / len(percentages)
                else:
                    completion_percentage = 0

            model = DestinyCatalystModel(
                name=catalyst.display_properties.name,
                complete=completion_percentage == 1,
                completion_percentage=completion_percentage,
                completion_status=make_progress_bar_text(completion_percentage),
            )

            # get the slot and sort them
            if DestinyPresentationNodeWeaponSlotEnum.KINETIC.value in catalyst.parent_node_hashes:
                result.kinetic.append(model)
            elif DestinyPresentationNodeWeaponSlotEnum.ENERGY.value in catalyst.parent_node_hashes:
                result.energy.append(model)
            elif DestinyPresentationNodeWeaponSlotEnum.POWER.value in catalyst.parent_node_hashes:
                result.power.append(model)

            # add to the total
            if model.complete:
                result.completed += 1

        return result

    async def get_used_vault_space(self) -> int:
        """Gets the current used vault space of the user"""

        buckets = await self.__get_inventory_bucket(DestinyInventoryBucketEnum.VAULT)

        return len(buckets[DestinyInventoryBucketEnum.VAULT])

    async def get_bright_dust(self) -> int:
        """Gets the current bright dust of the user"""

        return await self.__get_currency_amount(bucket=DestinyInventoryBucketEnum.BRIGHT_DUST)

    async def get_legendary_shards(self) -> int:
        """Gets the current legendary shards of the user"""

        return await self.__get_currency_amount(bucket=DestinyInventoryBucketEnum.SHARDS)

    async def get_consumable_amount(
        self, consumable_id: int, check_vault: bool = False, check_postmaster: bool = False
    ) -> int:
        """Returns the amount of a consumable this user has"""

        result = await self.__get_profile()
        items = list(result.character_currency_lookups.data.values())[0].item_quantities
        try:
            value = items[consumable_id]
        except KeyError:
            value = 0

        to_check = []
        if check_vault:
            to_check.append(DestinyInventoryBucketEnum.VAULT)
        if check_postmaster:
            to_check.append(DestinyInventoryBucketEnum.POSTMASTER)

        if to_check:
            buckets = await self.__get_inventory_bucket(*to_check)

            for bucket in buckets.values():
                if consumable_id in bucket:
                    value += bucket[consumable_id]["quantity"]

        return value

    async def get_max_power(self) -> float:
        """Returns the max power of the user"""

        char_data = await self.__get_all_inventory_bucket(include_item_level=True)

        # look at each character
        max_power = await to_thread.run_sync(lambda: get_max_power_subprocess(char_data=char_data))

        return max_power

    async def get_last_online(self) -> datetime.datetime:
        """Returns the last online time"""

        result = await self.__get_profile()
        return result.profile.data.date_last_played

    async def get_triumph_score(self) -> DestinyTriumphScoreModel:
        """Returns the triumph score"""

        triumphs_data = await self.get_triumphs()

        return DestinyTriumphScoreModel(
            active_score=triumphs_data["active_score"],
            legacy_score=triumphs_data["legacy_score"],
            lifetime_score=triumphs_data["lifetime_score"],
        )

    async def has_triumph(
        self, triumph_hash: str | int, send_details: bool = False, fresh_db: bool = False
    ) -> BoolModelRecord:
        """Returns if the triumph is gotten"""

        triumph_hash = int(triumph_hash)

        # check cache
        async with has_triumph_lock:
            if self.destiny_id not in cache.triumphs:
                cache.triumphs.update({self.destiny_id: set()})

            if triumph_hash not in cache.triumphs[self.destiny_id]:
                # check if the last update is older than 10 minutes
                if not send_details and (
                    self.user.triumphs_last_updated + datetime.timedelta(minutes=10) > get_now_with_tz()
                ):
                    return BoolModelRecord(bool=False)

                async with AsyncExitStack() as async_onexit_calls:
                    if fresh_db:
                        db = await async_onexit_calls.enter_async_context(acquire_db_session())
                    else:
                        db = self.db

                    # sync the cache with the db
                    results = await records.gotten_records(db=db, destiny_id=self.destiny_id)
                    if results and len(results) != len(cache.triumphs[self.destiny_id]):
                        # only caching already got records
                        for record in results:
                            cache.triumphs[self.destiny_id].add(record.record_id)
                        if triumph_hash in cache.triumphs[self.destiny_id]:
                            return BoolModelRecord(bool=True)

                    # alright, the user doesn't have the triumph, at least not in the db. So let's update the db entries
                    triumphs_data = await self.get_triumphs()
                    to_insert = []
                    sought_triumph = {}

                    # loop through all triumphs and add them / update them in the db
                    for triumph_id, triumph_info in triumphs_data.items():
                        try:
                            triumph_id = int(triumph_id)
                        except ValueError:
                            # this is the "active_score", ... fields
                            continue

                        if triumph_id in cache.triumphs[self.destiny_id]:
                            continue

                        # calculate if the triumph is gotten and save the triumph we are looking for
                        status = True
                        if not triumph_info.objectives:
                            status &= DestinyRecordState.OBJECTIVE_NOT_COMPLETED not in triumph_info.state

                        else:
                            for part in triumph_info.objectives:
                                status &= part.complete

                        # is this the triumph we are looking for?
                        if triumph_id == triumph_hash:
                            sought_triumph = triumph_info

                        # don't really need to insert not-gained triumphs
                        if status:
                            cache.triumphs[self.destiny_id].add(triumph_id)
                            to_insert.append(Records(destiny_id=self.destiny_id, record_id=triumph_id))

                    # mass insert the missing entries
                    if to_insert:
                        await records.insert_records(db=db, objs=to_insert)

                    # save the update time
                    await discord_users.update(db=db, to_update=self.user, triumphs_last_updated=get_now_with_tz())

        # now check again if its completed
        if triumph_hash in cache.triumphs[self.destiny_id]:
            return BoolModelRecord(bool=True)

        # if not, return the data with the objectives info
        result = BoolModelRecord(bool=False)
        if send_details:
            if sought_triumph.objectives:
                for part in sought_triumph.objectives:
                    result.objectives.append(BoolModelObjective(objective_id=part.objective_hash, bool=part.complete))
        return result

    async def has_collectible(self, collectible_hash: str | int, fresh_db: bool = False) -> bool:
        """Returns if the collectible is gotten"""

        collectible_hash = int(collectible_hash)

        # check cache
        async with has_collectible_lock:
            if self.destiny_id not in cache.collectibles:
                cache.collectibles.update({self.destiny_id: set()})

            if collectible_hash not in cache.collectibles[self.destiny_id]:
                # check if the last update is older than 10 minutes
                if self.user.collectibles_last_updated + datetime.timedelta(minutes=10) > get_now_with_tz():
                    return False

                async with AsyncExitStack() as async_onexit_calls:
                    if fresh_db:
                        db = await async_onexit_calls.enter_async_context(acquire_db_session())
                    else:
                        db = self.db

                    # sync the cache with the db
                    results = await collectibles.gotten_collectibles(db=db, destiny_id=self.destiny_id)
                    if results and len(results) != len(cache.collectibles[self.destiny_id]):
                        # only caching already got collectibles
                        for collectible in results:
                            cache.collectibles[self.destiny_id].add(collectible.collectible_id)
                        if collectible_hash in cache.collectibles[self.destiny_id]:
                            return True

                    # as with the triumphs, we need to update our local collectible data now
                    collectibles_data = await self.get_collectibles()
                    to_insert = []

                    # loop through the collectibles
                    for collectible_id, collectible_info in collectibles_data.items():
                        # if its in cache, its also in the db
                        if collectible_id in cache.collectibles[self.destiny_id]:
                            continue

                        # don't really need to insert not-owned collectibles
                        if DestinyCollectibleState.NOT_ACQUIRED not in collectible_info.state:
                            cache.collectibles[self.destiny_id].add(collectible_id)
                            to_insert.append(Collectibles(destiny_id=self.destiny_id, collectible_id=collectible_id))

                    # mass insert the missing entries
                    if to_insert:
                        await collectibles.insert_collectibles(db=db, objs=to_insert)

                    # save the update time
                    await discord_users.update(db=db, to_update=self.user, collectibles_last_updated=get_now_with_tz())

        # now check again if its owned
        return collectible_hash in cache.collectibles[self.destiny_id]

    async def get_metric_value(self, metric_hash: str | int) -> int:
        """Returns the value of the given metric hash"""

        metric_hash = int(metric_hash)
        metrics = await self.get_metrics()

        try:
            return metrics[metric_hash].objective_progress.progress
        except KeyError:
            raise CustomException("BungieDestinyItemNotExist")

    async def get_stat_value(
        self,
        stat_name: str,
        stat_category: Literal[
            "allTime",
            "allPvE",
            "allPvP",
        ] = "allTime",
        character_id: Optional[int | str] = None,
    ) -> int | float:
        """Returns the value of the given stat. Int if no decimals, else float"""

        possible_stat_categories = [
            "allTime",
            "allPvE",
            "allPvP",
        ]
        assert stat_category in possible_stat_categories, f"Stat must be one of {possible_stat_categories}"

        stats = await self.get_stats()

        # character stats
        if character_id:
            found = False
            for char in stats.characters:
                if char.character_id == int(character_id):
                    stats = char
                    found = True

            if not found:
                raise CustomException("CharacterIdNotFound")

        # total stats
        else:
            stats = stats.merged_all_characters

        if stat_category == "allTime":
            stats = stats.merged
        else:
            stats = stats.results[stat_category]

        stat = stats.all_time[stat_name].basic.value
        return int(stat) if stat.is_integer() else stat

    async def get_artifact_level(self) -> ValueModel:
        """Returns the seasonal artifact data"""

        result = await self.__get_profile()
        return ValueModel(value=result.profile_progression.data.seasonal_artifact.power_bonus)

    async def get_season_pass_level(self) -> ValueModel:
        """Returns the seasonal pass level"""

        result = await self.__get_profile()
        data = list(result.character_progressions.data.values())[0].progressions

        season_pass = await destiny_manifest.get_current_season_pass()

        return ValueModel(
            value=data[season_pass.reward_progression_hash].level + data[season_pass.prestige_progression_hash].level
        )

    async def get_seasonal_challenges(self) -> SeasonalChallengesModel:
        """Returns the seasonal challenges completion info"""

        user_sc = copy.deepcopy(await destiny_manifest.get_seasonal_challenges_definition())
        user_records = await self.get_triumphs()

        # now calculate the members completions status
        user_sc = await to_thread.run_sync(
            lambda: get_seasonal_challenges_subprocess(user_sc=user_sc, user_records=user_records)
        )

        return user_sc

    async def get_character_id_by_class(self, character_class: str) -> Optional[int]:
        """Return the matching character id if exists"""

        # make sure the class exists
        if not (character_class := getattr(DestinyClass, character_class.upper(), None)):
            return None

        # loop through the chars and return the matching one
        characters = await self.get_character_info()
        if characters:
            for character_data in characters.characters:
                if character_data.character_class == character_class.display_name:
                    return character_data.character_id
        return None

    async def get_character_ids(self) -> list[int]:
        """Return the character ids only"""

        characters = await self.get_character_info()

        ids = []
        if characters:
            for character_data in characters.characters:
                ids.append(character_data.character_id)
        return ids

    async def get_character_info(self) -> DestinyCharactersModel:
        """Get character info"""

        characters = DestinyCharactersModel()
        result = await self.__get_profile()

        # loop through each character
        for character_id, character_data in result.characters.data.items():
            # format the data correctly and convert the hashes to strings
            characters.characters.append(
                DestinyCharacterModel(
                    character_id=character_id,
                    character_class=character_data.class_type.display_name,
                    character_race=character_data.race_type.display_name,
                    character_gender=character_data.gender_type.display_name,
                )
            )

        return characters

    async def get_triumphs(self) -> dict[int | str, DestinyRecordComponent | int]:
        """Populate the triumphs and then return them"""

        if not self._triumphs:
            result = await self.__get_profile()

            # combine profile and character ones
            self._triumphs = await to_thread.run_sync(lambda: get_triumphs_subprocess(result=result))

        return self._triumphs

    async def get_collectibles(self) -> dict[int, DestinyCollectibleComponent]:
        """Populate the collectibles and then return them"""

        if not self._collectibles:
            result = await self.__get_profile()

            # combine profile and character ones
            self._collectibles = await to_thread.run_sync(lambda: get_collectibles_subprocess(result=result))
        return self._collectibles

    async def get_craftables(self) -> dict[int, DestinyCraftableComponent]:
        """Populate the craftables and then return them"""

        result = await self.__get_profile()
        return await to_thread.run_sync(lambda: get_craftables_subprocess(result=result))

    async def get_materials(self) -> DestinyAllMaterialsModel:
        """Get all noteworthy materials of the user"""

        materials = DestinyAllMaterialsModel()
        for item in [
            ["Glimmer", 3159615086, False, False],
            ["Legendary Shards", 1022552290, False, False],
            ["Bright Dust", 2817410917, False, False],
        ]:
            materials.basic.append(
                DestinyNamedValueItemModel(
                    reference_id=item[1],
                    name=item[0],
                    value=await self.get_consumable_amount(
                        consumable_id=item[1], check_vault=item[2], check_postmaster=item[3]
                    ),
                )
            )
        for item in [
            ["Spoils of Conquest", 3702027555, False, True],
            ["Raid Banner", 3282419336, True, False],
            ["Sweaty Confetti", 1643912408, False, False],
        ]:
            materials.special.append(
                DestinyNamedValueItemModel(
                    reference_id=item[1],
                    name=item[0],
                    value=await self.get_consumable_amount(
                        consumable_id=item[1], check_vault=item[2], check_postmaster=item[3]
                    ),
                )
            )
        for item in [
            ["Synthweave Strap (Hunter)", 4019412287, False, False],
            ["Synthweave Plate (Titan)", 4238733045, False, False],
            ["Synthweave Bolt (Warlock)", 1498161294, False, False],
        ]:
            materials.transmog.append(
                DestinyNamedValueItemModel(
                    reference_id=item[1],
                    name=item[0],
                    value=await self.get_consumable_amount(
                        consumable_id=item[1], check_vault=item[2], check_postmaster=item[3]
                    ),
                )
            )
        for item in [
            ["Resonant Alloy", 2497395625, False, False],
            ["Drowned Alloy", 2708128607, False, True],
            ["Ascendant Alloy", 353704689, False, True],
        ]:
            materials.crafting.append(
                DestinyNamedValueItemModel(
                    reference_id=item[1],
                    name=item[0],
                    value=await self.get_consumable_amount(
                        consumable_id=item[1], check_vault=item[2], check_postmaster=item[3]
                    ),
                )
            )
        for item in [
            ["Upgrade Module", 2979281381, False, True],
            ["Enhancement Core", 3853748946, False, False],
            ["Enhancement Prism", 4257549984, False, True],
            ["Ascendant Shard", 4257549985, False, True],
        ]:
            materials.upgrading.append(
                DestinyNamedValueItemModel(
                    reference_id=item[1],
                    name=item[0],
                    value=await self.get_consumable_amount(
                        consumable_id=item[1], check_vault=item[2], check_postmaster=item[3]
                    ),
                )
            )

        return materials

    async def get_metrics(self) -> dict[int, DestinyMetricComponent]:
        """Populate the metrics and then return them"""

        metrics = await self.__get_profile()
        return metrics.metrics.data.metrics

    async def get_stats(self) -> DestinyHistoricalStatsAccountResult:
        """Get destiny stats"""

        return await self.user.bungio_user.get_historical_stats_for_account(
            groups=[DestinyStatsGroupType.NONE], auth=self.user.auth
        )

    async def get_items_in_inventory_bucket(self, bucket: int) -> list[DestinyItemComponent]:
        """
        Returns all items in bucket. Default is vault hash, for others search "bucket" at https://data.destinysets.com/

        Some buckets that are important:
            Vault: 138197802
        """

        result = await self.__get_profile()
        all_items = result.profile_inventory.data.items
        items = []
        for item in all_items:
            if item.bucket_hash == bucket:
                items.append(item)

        return items

    async def get_time_played(
        self,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        mode: int = 0,
        activity_ids: Optional[list[int]] = None,
        character_class: Optional[str] = None,
    ) -> int:
        """Get the time played (in seconds)"""

        return await crud_activities.calculate_time_played(
            db=self.db,
            destiny_id=self.destiny_id,
            mode=mode,
            activity_ids=activity_ids,
            start_time=start_time,
            end_time=end_time,
            character_class=character_class,
        )

    async def __get_inventory_bucket(
        self, *buckets: DestinyInventoryBucketEnum
    ) -> dict[
        DestinyInventoryBucketEnum,
        dict[int, dict[Literal["item", "power_level", "quantity"], DestinyItemComponent | int]],
    ]:
        """
        Get all the items from an inventory bucket. Default: All buckets

        Returns:
        {
            DestinyInventoryBucketEnum: {
                item_hash: {
                    "item": item,
                    "power_level": power_level
                },
                ...
            },
            ...
        }
        """

        # default is vault
        if not buckets:
            buckets = DestinyInventoryBucketEnum.all()

        result = {}
        for bucket in buckets:
            if bucket not in self._inventory_bucket:
                profile = await self.__get_profile()

                # only get the items in the correct buckets
                self._inventory_bucket.update(
                    await to_thread.run_sync(lambda: get_inventory_bucket_subprocess(result=profile, buckets=buckets))
                )

            result[bucket] = self._inventory_bucket.get(bucket, {})

        return result

    async def __get_all_inventory_bucket(
        self, *buckets: DestinyInventoryBucketEnum, include_item_level: bool = False
    ) -> dict[
        int,
        dict[DestinyInventoryBucketEnum, dict[int, dict[Literal["item", "power_level"], DestinyItemComponent | int]]],
    ]:
        """
        Get all the items from an inventory bucket. Includes both profile and character. Default: All buckets
        Includes the power level is asked for under "power_level"

        Returns:
        {
            character_id: {
                DestinyInventoryBucketEnum: {
                    itemInstanceId: itemComponents_data,
                    ...
                },
                ...
            },
            ...
        }
        """

        def add_info(
            result_dict: dict[
                int,
                dict[
                    DestinyInventoryBucketEnum,
                    dict[int, dict[Literal["item", "power_level"], DestinyItemComponent | int]],
                ],
            ],
            item: DestinyItemComponent,
            char_id: int,
        ):
            """Func to add the items"""

            # only get the items in the correct buckets
            for bucket in buckets:
                if item.bucket_hash == bucket.value:
                    if bucket not in result_dict[char_id]:
                        result_dict[char_id].update({bucket: {}})
                    result_dict[char_id][bucket].update({item.item_instance_id: {"item": item}})
                    if include_item_level:
                        try:
                            result_dict[char_id][bucket][item.item_instance_id][
                                "power_level"
                            ] = result.item_components.instances.data[item.item_instance_id].primary_stat.value
                        except KeyError:
                            pass
                    break

        # default is vault
        if not buckets:
            buckets = DestinyInventoryBucketEnum.all()

        result = await self.__get_profile()
        items: dict[
            int,
            dict[
                DestinyInventoryBucketEnum, dict[int, dict[Literal["item", "power_level"], DestinyItemComponent | int]]
            ],
        ] = {}

        # first get the character ids and their class
        character_ids = {}
        for character_id, character_data in result.characters.data.items():
            class_type = character_data.class_type
            if class_type not in character_ids:
                character_ids.update({class_type: [character_id]})
            else:
                character_ids[class_type].append(character_id)

        # get character inventory
        for character_id, character_data in result.character_inventories.data.items():
            if character_id not in items:
                items.update({character_id: {}})

            for inv_item in character_data.items:
                await to_thread.run_sync(lambda: add_info(result_dict=items, item=inv_item, char_id=character_id))

        # get character equipped
        for character_id, character_data in result.character_equipment.data.items():
            for inv_item in character_data.items:
                await to_thread.run_sync(lambda: add_info(result_dict=items, item=inv_item, char_id=character_id))

        # get stuff in vault that is character specific
        for profile_data in result.profile_inventory.data.items:
            # only check if it has a instance id and is in the correct bucket
            if profile_data.bucket_hash == DestinyInventoryBucketEnum.VAULT.value and profile_data.item_instance_id:
                # get the character class and actual bucket hash from the item id
                definition = await destiny_manifest.get_item(item_id=profile_data.item_hash)
                profile_data.bucket_hash = definition.inventory.bucket_type_hash

                # try to catch users which deleted their warlock but still have warlock items
                if definition.class_type in character_ids:
                    # add the data to each character
                    actual_character_ids = character_ids[definition.class_type]
                    for actual_character_id in actual_character_ids:
                        await to_thread.run_sync(
                            lambda: add_info(result_dict=items, item=profile_data, char_id=actual_character_id)
                        )

        return items

    async def __get_profile(self) -> DestinyProfileResponse:
        """
        Return info from the profile call
        https://bungie-net.github.io/multi/schema_Destiny-DestinyComponentType.html#schema_Destiny-DestinyComponentType
        """
        if not self._profile:
            # just calling nearly all of them. Don't need all quite yet, but who knows what the future will bring
            components = [
                100,
                101,
                102,
                103,
                104,
                105,
                200,
                201,
                202,
                204,
                205,
                300,
                301,
                302,
                304,
                305,
                306,
                307,
                400,
                401,
                402,
                500,
                600,
                700,
                800,
                900,
                1100,
                1200,
                1300,
            ]

            self._profile = await self.user.bungio_user.get_profile(components=components, auth=self.user.auth)

            # get bungie name
            bungie_name = self._profile.profile.data.user_info.full_bungie_name

            # update name if different
            if bungie_name != self.user.bungie_name:
                await discord_users.update(db=self.db, to_update=self.user, bungie_name=bungie_name)

        return self._profile

    async def __get_currency_amount(self, bucket: DestinyInventoryBucketEnum) -> int:
        """Returns the amount of the specified currency owned"""

        profile = await self.__get_profile()
        items = profile.profile_currencies.data.items

        # get the item with the correct bucket
        value = 0
        for item in items:
            if item.bucket_hash == bucket.value:
                value = item.quantity
        return value


def get_max_power_subprocess(
    char_data: dict[
        int,
        dict[DestinyInventoryBucketEnum, dict[int, dict[Literal["item", "power_level"], DestinyItemComponent | int]]],
    ]
) -> int:
    """Run in anyio subprocess on another thread since this might be slow"""

    max_power = 0
    for character in char_data:
        helmet = 0
        gauntlet = 0
        chest = 0
        leg = 0
        class_item = 0

        kinetic = 0
        energy = 0
        power = 0

        for bucket, data in char_data[character].items():
            # save the items light level
            for item_id, item_data in data.items():
                match bucket:
                    case DestinyInventoryBucketEnum.HELMET:
                        if item_data["power_level"] > helmet:
                            helmet = item_data["power_level"]
                    case DestinyInventoryBucketEnum.GAUNTLETS:
                        if item_data["power_level"] > gauntlet:
                            gauntlet = item_data["power_level"]
                    case DestinyInventoryBucketEnum.CHEST:
                        if item_data["power_level"] > chest:
                            chest = item_data["power_level"]
                    case DestinyInventoryBucketEnum.LEG:
                        if item_data["power_level"] > leg:
                            leg = item_data["power_level"]
                    case DestinyInventoryBucketEnum.CLASS:
                        if item_data["power_level"] > class_item:
                            class_item = item_data["power_level"]
                    case DestinyInventoryBucketEnum.KINETIC:
                        if item_data["power_level"] > kinetic:
                            kinetic = item_data["power_level"]
                    case DestinyInventoryBucketEnum.ENERGY:
                        if item_data["power_level"] > energy:
                            energy = item_data["power_level"]
                    case DestinyInventoryBucketEnum.POWER:
                        if item_data["power_level"] > power:
                            power = item_data["power_level"]

        # get the max power
        char_max_power = (helmet + gauntlet + chest + leg + class_item + kinetic + energy + power) / 8
        if char_max_power > max_power:
            max_power = char_max_power

    return max_power


def get_seasonal_challenges_subprocess(
    user_sc: SeasonalChallengesModel, user_records: dict[int | str, DestinyRecordComponent | int]
) -> SeasonalChallengesModel:
    """Run in anyio subprocess on another thread since this might be slow"""

    for topic in user_sc.topics:
        for sc in topic.seasonal_challenges:
            record = user_records[sc.record_id]

            # calculate completion rate
            rate = []
            for objective in record.objectives:
                try:
                    rate.append(objective.progress / objective.completion_value if not objective.complete else 1)
                except ZeroDivisionError:
                    # the item is classified
                    rate.append(0)
            percentage = sum(rate) / len(rate)

            # make emoji art for completion rate
            sc.completion_percentage = percentage
            sc.completion_status = make_progress_bar_text(percentage)

    return user_sc


def get_triumphs_subprocess(result: DestinyProfileResponse) -> dict[int | str, DestinyRecordComponent | int]:
    """Run in anyio subprocess on another thread since this might be slow"""

    # get profile triumphs
    triumphs = result.profile_records.data.records
    # noinspection PyTypeChecker
    triumphs.update(
        {
            "active_score": result.profile_records.data.active_score,
            "legacy_score": result.profile_records.data.legacy_score,
            "lifetime_score": result.profile_records.data.lifetime_score,
        }
    )

    # get character triumphs
    character_triumphs = [
        character_triumphs.records for character_id, character_triumphs in result.character_records.data.items()
    ]

    # combine them
    for triumph in character_triumphs:
        triumphs.update(triumph)

    return triumphs


def get_collectibles_subprocess(result: DestinyProfileResponse) -> dict[int, DestinyCollectibleComponent]:
    """Run in anyio subprocess on another thread since this might be slow"""

    # get profile collectibles
    user_collectibles = result.profile_collectibles.data.collectibles

    # get character collectibles
    character_collectibles = [
        character_triumphs.collectibles for _, character_triumphs in result.character_collectibles.data.items()
    ]

    # combine them
    for character in character_collectibles:
        # loop through all the collectibles and only update them if the collectible is earned
        for collectible_hash, collectible in character.items():
            if DestinyCollectibleState.NOT_ACQUIRED not in collectible.state:
                user_collectibles.update({collectible_hash: collectible})

    return user_collectibles


def get_craftables_subprocess(result: DestinyProfileResponse) -> dict[int, DestinyCraftableComponent]:
    """Run in anyio subprocess on another thread since this might be slow"""

    # get profile craftables
    user_craftables = {}

    # get character craftables
    character_craftables = [
        character_info.craftables for _character_id, character_info in result.character_craftables.data.items()
    ]

    # combine them
    for character in character_craftables:
        # loop through all the craftables and only update them if the collectible is earned
        for craftable_hash, craftable in character.items():
            user_craftables[craftable_hash] = craftable

    return user_craftables


def get_inventory_bucket_subprocess(
    result: DestinyProfileResponse, buckets: list[DestinyInventoryBucketEnum]
) -> dict[
    DestinyInventoryBucketEnum, dict[int, dict[Literal["item", "power_level", "quantity"], DestinyItemComponent | int]]
]:
    """Run in anyio subprocess on another thread since this might be slow"""

    def check_bucket():
        for bucket in buckets:
            if item.bucket_hash == bucket.value:
                item_hash = item.item_hash
                if bucket not in items:
                    items[bucket] = {}

                # unique items
                if item_hash not in items[bucket]:
                    try:
                        power_level = result.item_components.instances.data[item_hash].primary_stat.value
                    except KeyError:
                        power_level = 0

                    items[bucket][item_hash] = {
                        "item": item,
                        "power_level": power_level,
                        "quantity": item.quantity,
                    }

                    break
                # stackables, like enhancement prims
                else:
                    items[bucket][item_hash]["quantity"] += item.quantity

    items = {}

    # profile items
    for item in result.profile_inventory.data.items:
        check_bucket()

    if DestinyInventoryBucketEnum.POSTMASTER in buckets:
        # character items
        for data in result.character_inventories.data.values():
            for item in data.items:
                check_bucket()

    return items
