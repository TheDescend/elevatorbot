import asyncio
import dataclasses
import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud import crud_activities, destiny_manifest, discord_users
from Backend.crud.destiny.collectibles import collectibles
from Backend.crud.destiny.items import destiny_items
from Backend.crud.destiny.records import records
from Backend.database.models import (
    Collectibles,
    DestinyPresentationNodeDefinition,
    DestinyRecordDefinition,
    DiscordUsers,
    Records,
)
from Backend.misc.cache import cache
from Backend.misc.helperFunctions import (
    get_datetime_from_bungie_entry,
    get_now_with_tz,
    make_progress_bar_text,
)
from Backend.networking.bungieApi import BungieApi
from Backend.networking.bungieRoutes import profile_route, stat_route
from DestinyEnums.enums import (
    DestinyInventoryBucketEnum,
    DestinyPresentationNodeWeaponSlotEnum,
)
from NetworkingSchemas.basic import ValueModel
from NetworkingSchemas.destiny.account import (
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
    SeasonalChallengesRecordModel,
    SeasonalChallengesTopicsModel,
)

# todo check usage of ALL functions


@dataclasses.dataclass
class DestinyProfile:
    """User specific API calls"""

    db: AsyncSession
    user: DiscordUsers

    race_map = {2803282938: "Awoken", 898834093: "Exo", 3887404748: "Human"}
    gender_map = {
        2204441813: "Female",
        3111576190: "Male",
    }
    class_map = {671679327: "Hunter", 2271682572: "Warlock", 3655393761: "Titan"}

    _triumphs: dict = dataclasses.field(init=False, default_factory=dict)

    def __post_init__(self):
        # some shortcuts
        self.discord_id = self.user.discord_id
        self.destiny_id = self.user.destiny_id
        self.system = self.user.system

        # the network class
        self.api = BungieApi(db=self.db, user=self.user)

    async def get_seal_completion(self) -> DestinySealsModel:
        """Gets all seals and the users completion status"""

        # get the seals
        seals = await destiny_items.get_seals(db=self.db)

        # loop through the seals and format the data
        result = DestinySealsModel()
        for seal, triumphs in seals.items():
            # get user completion
            user_guilded_completed = []
            user_guilded_completed_int = 0
            user_completed = []
            user_completed_int = 0
            for triumph in triumphs:
                user_data = await self.has_triumph(triumph.reference_id)
                model = DestinyRecordModel(
                    name=triumph.name,
                    description=triumph.description,
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
            data = DestinySealModel(
                name=seal.name,
                description=seal.description,
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
                    name=seal.name,
                    description=seal.description,
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

        catalysts = await destiny_items.get_catalysts(db=self.db)
        triumphs = await self.get_triumphs()

        # check their completion
        result = DestinyCatalystsModel()
        for catalyst in catalysts:
            user_data = triumphs[str(catalyst.reference_id)]["objectives"]

            # get the completion rate
            complete = user_data["complete"]
            if complete:
                completion_percentage = 1
            elif user_data["completionValue"]:
                completion_percentage = user_data["progress"] / user_data["completionValue"]
            else:
                completion_percentage = 0

            model = DestinyCatalystModel(
                name=catalyst.name,
                complete=complete,
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
            if complete:
                result.completed += 1

        return result

    async def get_used_vault_space(self) -> int:
        """Gets the current used vault space of the user"""

        buckets = await self.__get_profile_inventory_bucket(DestinyInventoryBucketEnum.VAULT)

        return len(buckets[DestinyInventoryBucketEnum.VAULT])

    async def get_bright_dust(self) -> int:
        """Gets the current bright dust of the user"""

        return await self.__get_currency_amount(bucket=DestinyInventoryBucketEnum.BRIGHT_DUST)

    async def get_legendary_shards(self) -> int:
        """Gets the current legendary shards of the user"""

        return await self.__get_currency_amount(bucket=DestinyInventoryBucketEnum.SHARDS)

    async def get_consumable_amount(self, consumable_id: int) -> int:
        """Returns the amount of a consumable this user has"""

        buckets = await self.__get_profile_inventory_bucket(
            DestinyInventoryBucketEnum.VAULT, DestinyInventoryBucketEnum.CONSUMABLES
        )

        # get the value
        value = 0
        for bucket in buckets.values():
            if consumable_id in bucket:
                value += bucket[consumable_id]["quantity"]

        return value

    async def get_max_power(self) -> float:
        """Returns the max power of the user"""

        char_data = await self.__get_all_inventory_bucket(include_item_level=True)

        # look at each character
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

            # todo this does not work, since the bucket hash is defined by where the item is not by its type
            # todo plan: create a cache {itemHash: armour slot hash}. asyncio lock it the first time and get it from the DB
            for buckets in char_data[character]:
                # save the items light level
                for bucket, items in buckets.items():
                    match bucket:
                        case DestinyInventoryBucketEnum.HELMET:
                            if items["power_level"] > helmet:
                                helmet += items["power_level"]
                        case DestinyInventoryBucketEnum.GAUNTLETS:
                            if items["power_level"] > gauntlet:
                                gauntlet += items["power_level"]
                        case DestinyInventoryBucketEnum.CHEST:
                            if items["power_level"] > chest:
                                chest += items["power_level"]
                        case DestinyInventoryBucketEnum.LEG:
                            if items["power_level"] > leg:
                                leg += items["power_level"]
                        case DestinyInventoryBucketEnum.CLASS:
                            if items["power_level"] > class_item:
                                class_item += items["power_level"]
                        case DestinyInventoryBucketEnum.KINETIC:
                            if items["power_level"] > kinetic:
                                kinetic += items["power_level"]
                        case DestinyInventoryBucketEnum.ENERGY:
                            if items["power_level"] > energy:
                                energy += items["power_level"]
                        case DestinyInventoryBucketEnum.POWER:
                            if items["power_level"] > power:
                                power += items["power_level"]

            # get the max power
            char_max_power = (helmet + gauntlet + chest + leg + class_item + kinetic + energy + power) / 8
            if char_max_power > max_power:
                max_power = char_max_power

        return max_power

    async def get_last_online(self) -> datetime.datetime:
        """Returns the last online time"""

        result = await self.__get_profile()
        return get_datetime_from_bungie_entry(result["profile"]["data"]["dateLastPlayed"])

    async def get_triumph_score(self) -> DestinyTriumphScoreModel:
        """Returns the triumph score"""

        triumphs_data = await self.get_triumphs()

        return DestinyTriumphScoreModel(
            active_score=triumphs_data["active_score"],
            legacy_score=triumphs_data["legacy_score"],
            lifetime_score=triumphs_data["lifetime_score"],
        )

    async def has_triumph(self, triumph_hash: str | int) -> BoolModelRecord:
        """Returns if the triumph is gotten"""

        triumph_hash = int(triumph_hash)

        # check cache
        async with asyncio.Lock():
            if self.destiny_id not in cache.triumphs:
                cache.triumphs.update({self.destiny_id: {}})

            if triumph_hash not in cache.triumphs[self.destiny_id]:
                # check if the last update is older than 10 minutes
                if self._triumphs and (
                    self.user.triumphs_last_updated + datetime.timedelta(minutes=10) > get_now_with_tz()
                ):
                    sought_triumph = self._triumphs[str(triumph_hash)]

                else:
                    # get from db and return that if it says user got the triumph
                    result = await records.has_record(db=self.db, destiny_id=self.destiny_id, triumph_hash=triumph_hash)
                    if result:
                        # only caching already got triumphs
                        cache.triumphs[self.destiny_id].update({triumph_hash: True})
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

                        # does the entry exist in the db?
                        # we don't need to re calc the state if its already marked as earned in the db
                        result = await records.get_record(
                            db=self.db, destiny_id=self.destiny_id, triumph_hash=triumph_id
                        )
                        if result and result.completed:
                            cache.triumphs[self.destiny_id].update({triumph_id: True})
                            continue

                        # calculate if the triumph is gotten and save the triumph we are looking for
                        status = True
                        if "objectives" not in triumph_info:
                            # make sure it's RewardUnavailable aka legacy
                            assert triumph_info["state"] & 2

                            # https://bungie-net.github.io/multi/schema_Destiny-DestinyRecordState.html#schema_Destiny-DestinyRecordState
                            status &= triumph_info["state"] & 1

                        else:
                            for part in triumph_info["objectives"]:
                                status &= part["complete"]

                        # is this the triumph we are looking for?
                        if triumph_id == triumph_hash:
                            sought_triumph = triumph_info

                        # don't really need to insert not-gained triumphs
                        if status:
                            cache.triumphs[self.destiny_id].update({triumph_id: True})
                            # do we need to update or insert?
                            if not result:
                                # insert
                                to_insert.append(
                                    Records(destiny_id=self.destiny_id, record_id=triumph_id, completed=True)
                                )

                            else:
                                # update
                                await records.update_record(db=self.db, obj=result, completed=True)

                    # mass insert the missing entries
                    if to_insert:
                        await records.insert_records(db=self.db, objs=to_insert)

                    # save the update time
                    await discord_users.update(db=self.db, to_update=self.user, triumphs_last_updated=get_now_with_tz())

        # now check again if its completed
        if triumph_hash in cache.triumphs[self.destiny_id]:
            return BoolModelRecord(bool=True)

        # if not, return the data with the objectives info
        result = BoolModelRecord(bool=False)
        if "objectives" in sought_triumph:
            for part in sought_triumph["objectives"]:
                result.objectives.append(BoolModelObjective(objective_id=part["objectiveHash"], bool=part["complete"]))
        return result

    async def has_collectible(self, collectible_hash: str | int) -> bool:
        """Returns if the collectible is gotten"""

        collectible_hash = int(collectible_hash)

        # check cache
        async with asyncio.Lock():
            if self.destiny_id not in cache.collectibles:
                cache.collectibles.update({self.destiny_id: {}})

            if collectible_hash not in cache.collectibles[self.destiny_id]:
                # check if the last update is older than 10 minutes
                if self.user.collectibles_last_updated + datetime.timedelta(minutes=10) > get_now_with_tz():
                    return False

                # get from db and return that if it says user got the collectible
                result = await collectibles.has_collectible(
                    db=self.db, destiny_id=self.destiny_id, collectible_hash=collectible_hash
                )
                if result:
                    # only caching already got collectibles
                    cache.collectibles[self.destiny_id].update({collectible_hash: True})
                    return True

                # as with the triumphs, we need to update our local collectible data now
                collectibles_data = await self.get_collectibles()
                to_insert = []

                # loop through the collectibles
                for collectible_id, collectible_info in collectibles_data.items():
                    collectible_id = int(collectible_id)

                    if collectible_id in cache.collectibles[self.destiny_id]:
                        continue

                    # does the entry exist in the db?
                    # we don't need to re calc the state if its already marked as owned in the db
                    result = await collectibles.get_collectible(
                        db=self.db, destiny_id=self.destiny_id, collectible_hash=collectible_id
                    )
                    if result and result.owned:
                        cache.collectibles[self.destiny_id].update({collectible_id: True})
                        continue

                    # bit 1 not being set means the collectible is gotten
                    # see https://bungie-net.github.io/multi/schema_Destiny-DestinyCollectibleState.html#schema_Destiny-DestinyCollectibleState
                    status = collectible_info["state"] & 1 == 0

                    # don't really need to insert not-owned collectibles
                    if status:
                        cache.collectibles[self.destiny_id].update({collectible_id: True})
                        # do we need to update or insert?
                        if not result:
                            # insert
                            to_insert.append(
                                Collectibles(destiny_id=self.destiny_id, collectible_id=collectible_id, owned=True)
                            )

                        else:
                            # update
                            await collectibles.update_collectible(db=self.db, obj=result, owned=True)

                # mass insert the missing entries
                if to_insert:
                    await collectibles.insert_collectibles(db=self.db, objs=to_insert)

                # save the update time
                await discord_users.update(db=self.db, to_update=self.user, collectibles_last_updated=get_now_with_tz())

        # now check again if its owned
        if collectible_hash in cache.collectibles[self.destiny_id]:
            return True
        else:
            return False

    async def get_metric_value(self, metric_hash: str | int) -> int:
        """Returns the value of the given metric hash"""

        metric_hash = str(metric_hash)
        metrics = await self.get_metrics()

        try:
            return metrics[metric_hash]["objectiveProgress"]["progress"]
        except KeyError:
            raise CustomException("BungieDestinyItemNotExist")

    async def get_stat_value(
        self,
        stat_name: str,
        stat_category: str = "allTime",
        character_id: Optional[int | str] = None,
    ) -> int | float:
        """Returns the value of the given stat. Int if no decimals, else float"""

        possible_stat_categories = [
            "allTime",
            "allPvE",
            "allPvP",
        ]
        assert stat_category in possible_stat_categories, f"Stat must be one of {possible_stat_categories}"
        topic = "merged" if stat_category == "allTime" else "results"

        stats = await self.get_stats()

        # character stats
        if character_id:
            found = False
            for char in stats["characters"]:
                if char["characterId"] == str(character_id):
                    stats = char
                    found = True

            if not found:
                raise CustomException("CharacterIdNotFound")

        # total stats
        else:
            stats = stats["mergedAllCharacters"]

        stats = stats[topic][stat_category]
        if stat_category != "allTime":
            stats = stats["allTime"]
        stat: float = stats[stat_name]["basic"]["value"]
        return int(stat) if stat.is_integer() else stat

    async def get_artifact_level(self) -> ValueModel:
        """Returns the seasonal artifact data"""

        result = await self.__get_profile()
        return ValueModel(value=result["profileProgression"]["data"]["seasonalArtifact"]["powerBonus"])

    async def get_season_pass_level(self) -> ValueModel:
        """Returns the seasonal pass level"""

        # get the current season pass hash
        async with asyncio.Lock():
            if not cache.season_pass_definition:
                cache.season_pass_definition = await destiny_manifest.get_current_season_pass(db=self.db)

        # get a character id since they are character specific
        character_id = (await self.get_character_ids())[0]

        result = await self.__get_profile()
        character_data = result["characterProgressions"]["data"][str(character_id)]["progressions"]
        return ValueModel(
            value=character_data[str(cache.season_pass_definition.reward_progression_hash)]["level"]
            + character_data[str(cache.season_pass_definition.prestige_progression_hash)]["level"]
        )

    async def get_seasonal_challenges(self) -> SeasonalChallengesModel:
        """Returns the seasonal challenges completion info"""

        # do we have the info cached?
        async with asyncio.Lock():
            if not cache.seasonal_challenges_definition:
                definition = SeasonalChallengesModel()

                # get the info from the db
                sc_category_hash = 3443694067
                sc_presentation_node = await destiny_manifest.get(
                    db=self.db, table=DestinyPresentationNodeDefinition, primary_key=sc_category_hash
                )

                # loop through those categories and get the "Weekly" one
                for category_hash in sc_presentation_node.children_presentation_node_hash:
                    category = await destiny_manifest.get(
                        db=self.db, table=DestinyPresentationNodeDefinition, primary_key=category_hash
                    )

                    if category.name == "Weekly":
                        # loop through the seasonal challenges topics (Week1, Week2, etc...)
                        for sc_topic_hash in category.children_presentation_node_hash:
                            sc_topic = await destiny_manifest.get(
                                db=self.db, table=DestinyPresentationNodeDefinition, primary_key=sc_topic_hash
                            )

                            topic = SeasonalChallengesTopicsModel(name=sc_topic.name)

                            # loop through the actual seasonal challenges
                            for sc_hash in sc_topic.children_record_hash:
                                sc = await destiny_manifest.get(
                                    db=self.db, table=DestinyRecordDefinition, primary_key=sc_hash
                                )

                                topic.seasonal_challenges.append(
                                    SeasonalChallengesRecordModel(
                                        record_id=sc.reference_id, name=sc.name, description=sc.description
                                    )
                                )

                            definition.topics.append(topic)
                        break

                cache.seasonal_challenges_definition = definition

        user_sc = cache.seasonal_challenges_definition.copy()
        user_records = await self.get_triumphs()

        # now calculate the members completions status
        for topic in user_sc.topics:
            for sc in topic.seasonal_challenges:
                record = user_records[str(sc.record_id)]

                # calculate completion rate
                rate = []
                for objective in record["objectives"]:
                    rate.append(
                        objective["progress"] / objective["completionValue"] if not objective["complete"] else 1
                    )
                percentage = sum(rate) / len(rate)

                # make emoji art for completion rate
                sc.completion_percentage = percentage
                sc.completion_status = make_progress_bar_text(percentage)

        return user_sc

    async def get_character_id_by_class(self, character_class: str) -> Optional[int]:
        """Return the matching character id if exists"""

        # make sure the class exists
        class_names = list(self.class_map.values())
        if character_class not in class_names:
            return None

        # loop through the chars and return the matching one
        characters = await self.get_character_info()
        if characters:
            for character_data in characters.characters:
                if character_data.character_class == character_class:
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
        for character_id, character_data in result["characters"]["data"].items():
            character_id = int(character_id)

            # format the data correctly and convert the hashes to strings
            characters.characters.append(
                DestinyCharacterModel(
                    character_id=character_id,
                    character_class=self.class_map[character_data["classHash"]],
                    character_race=self.race_map[character_data["raceHash"]],
                    character_gender=self.gender_map[character_data["genderHash"]],
                )
            )

        return characters

    async def get_triumphs(self) -> dict:
        """Populate the triumphs and then return them"""

        result = await self.__get_profile()

        # get profile triumphs
        triumphs = result["profileRecords"]["data"]["records"]
        triumphs.update(
            {
                "active_score": result["profileRecords"]["data"]["activeScore"],
                "legacy_score": result["profileRecords"]["data"]["legacyScore"],
                "lifetime_score": result["profileRecords"]["data"]["lifetimeScore"],
            }
        )

        # get character triumphs
        character_triumphs = [
            character_triumphs["records"]
            for character_id, character_triumphs in result["characterRecords"]["data"].items()
        ]

        # combine them
        for triumph in character_triumphs:
            triumphs.update(triumph)

        self._triumphs = triumphs
        return self._triumphs

    async def get_collectibles(self) -> dict:
        """Populate the collectibles and then return them"""

        result = await self.__get_profile()

        # get profile triumphs
        user_collectibles = result["profileCollectibles"]["data"]["collectibles"]

        # get character triumphs
        character_collectibles = [
            character_triumphs["collectibles"]
            for _, character_triumphs in result["characterCollectibles"]["data"].items()
        ]

        # combine them
        for character in character_collectibles:
            # loop through all the collectibles and only update them if the collectible is earned
            # see https://bungie-net.github.io/multi/schema_Destiny-DestinyCollectibleState.html#schema_Destiny-DestinyCollectibleState
            for collectible_hash, collectible_state in character.items():
                if collectible_state["state"] & 1 == 0:
                    user_collectibles.update({collectible_hash: collectible_state})

        return user_collectibles

    async def get_metrics(self) -> dict:
        """Populate the metrics and then return them"""

        metrics = await self.__get_profile()
        return metrics["metrics"]["data"]["metrics"]

    async def get_stats(self) -> dict:
        """Get destiny stats"""

        route = stat_route.format(system=self.system, destiny_id=self.destiny_id)
        result = await self.api.get(route=route)
        return result.content

    async def get_items_in_inventory_bucket(self, bucket: int) -> list:
        """
        Returns all items in bucket. Default is vault hash, for others search "bucket" at https://data.destinysets.com/

        Some buckets that are important:
            Vault: 138197802
        """

        result = await self.__get_profile()
        all_items = result["profileInventory"]["data"]["items"]
        items = []
        for item in all_items:
            if item["bucketHash"] == bucket:
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
    ) -> dict[DestinyInventoryBucketEnum, dict[int, dict]]:
        """
        Get all the items from an inventory bucket. Default: All buckets

        Returns:
        {
            DestinyInventoryBucketEnum: {
                item_hash: dict_data,
                ...
            },
            ...
        }
        """

        # default is vault
        if not buckets:
            buckets = DestinyInventoryBucketEnum.all

        result = await self.__get_profile()

        items = {}

        # only get the items in the correct buckets
        if buckets != DestinyInventoryBucketEnum.all:
            for item in result["profileInventory"]["data"]["items"]:
                for bucket in buckets:
                    if item["bucketHash"] == bucket.value:
                        if bucket not in items:
                            items.update({bucket: {}})
                        items[bucket].update({item["itemHash"]: item})

        # get all buckets
        else:
            for item in result["profileInventory"]["data"]["items"]:
                if item["bucketHash"] not in items:
                    items.update({item["bucketHash"]: {}})
                items[item["bucketHash"]].update({item["itemHash"]: item})

        return items

    async def __get_profile_inventory_bucket(
        self, *buckets: DestinyInventoryBucketEnum
    ) -> dict[DestinyInventoryBucketEnum, dict[int, dict]]:
        """
        Get all the items from an inventory bucket. Default: All buckets

        Returns:
        {
            DestinyInventoryBucketEnum: {
                item_hash: dict_data,
                ...
            },
            ...
        }
        """

        # default is vault
        if not buckets:
            buckets = DestinyInventoryBucketEnum.all

        result = await self.__get_profile()

        items = {}

        # only get the items in the correct buckets
        for item in result["profileInventory"]["data"]["items"]:
            for bucket in buckets:
                if item["bucketHash"] == bucket.value:
                    item_hash = int(item["itemHash"])
                    if bucket not in items:
                        items.update({bucket: {}})
                    items[bucket].update({item_hash: item})
                    try:
                        items[bucket][item_hash].update(
                            {
                                "power_level": result["itemComponents"]["instances"]["data"][str(item_hash)][
                                    "primaryStat"
                                ]["value"]
                            }
                        )
                    except KeyError:
                        pass
                    break

        return items

    async def __get_all_inventory_bucket(
        self, *buckets: DestinyInventoryBucketEnum, include_item_level: bool = False
    ) -> dict[int, dict[DestinyInventoryBucketEnum, dict[int, dict]]]:
        """
        Get all the items from an inventory bucket. Includes both profile and character. Default: All buckets
        Includes the power level is asked for under "power_level"

        Returns:
        {
            character_id: {
                DestinyInventoryBucketEnum: {
                    item_hash: dict_data,
                    ...
                },
                ...
            },
            ...
        }
        """

        # default is vault
        if not buckets:
            buckets = DestinyInventoryBucketEnum.all

        result = await self.__get_profile()
        items = {}

        # first get the character ids and their class
        character_ids = {}
        for character_id, character_data in result["characters"]["data"].items():
            class_type = character_data["classType"]
            if class_type not in character_ids:
                character_ids.update({class_type: [int(character_id)]})
            else:
                character_ids[class_type].append(int(character_id))

        # func to add the items
        def add_info(result_dict: dict, item: dict, char_id: int):
            # only get the items in the correct buckets
            for bucket in buckets:
                if item["bucketHash"] == bucket.value:
                    item_hash = int(item["itemHash"])
                    if bucket not in result_dict[char_id]:
                        result_dict[char_id].update({bucket: {}})
                    result_dict[char_id][bucket].update({item_hash: item})
                    if include_item_level:
                        try:
                            result_dict[char_id][bucket][item_hash].update(
                                {
                                    "power_level": result["itemComponents"]["instances"]["data"][str(item_hash)][
                                        "primaryStat"
                                    ]["value"]
                                }
                            )
                        except KeyError:
                            pass
                    break

        # get character inventory
        for character_id, character_data in result["characterInventories"]["data"].items():
            character_id = int(character_id)
            if character_id not in items:
                items.update({character_id: {}})

            for inv_item in character_data["items"]:
                add_info(items, inv_item, character_id)

        # get character equipped
        for character_id, character_data in result["characterEquipment"]["data"].items():
            character_id = int(character_id)
            for inv_item in character_data["items"]:
                add_info(items, inv_item, character_id)

        # get stuff in vault that is character specific
        for profile_data in result["profileInventory"]["data"]:
            # only check if it has a instance id and is in the correct bucket
            if (
                profile_data["bucketHash"] == DestinyInventoryBucketEnum.VAULT.value
                and "itemInstanceId" in profile_data
            ):
                # get the character class from the item id
                definition = await destiny_items.get_item()

                actual_bucket_hash = definition.bucket_type_hash
                actual_character_ids = character_ids[definition.class_type]
                for actual_character_id in actual_character_ids:
                    items[actual_character_id][actual_bucket_hash].update({profile_data["itemHash"]: profile_data})
                    if include_item_level:
                        try:
                            items[actual_character_id][actual_bucket_hash][profile_data["itemHash"]].update(
                                {
                                    "power_level": result["itemComponents"]["instances"]["data"][
                                        str(profile_data["itemHash"])
                                    ]["primaryStat"]["value"]
                                }
                            )
                        except KeyError:
                            pass

        return items

    async def __get_profile(self) -> dict:
        """
        Return info from the profile call
        https://bungie-net.github.io/multi/schema_Destiny-DestinyComponentType.html#schema_Destiny-DestinyComponentType
        """
        # just calling nearly all of them. Don't need all quite yet, but who knows what the future will bring
        components = (
            100,
            101,
            102,
            103,
            104,
            105,
            200,
            201,
            202,
            203,
            204,
            205,
            300,
            301,
            302,
            303,
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
        )

        route = profile_route.format(system=self.system, destiny_id=self.destiny_id)
        params = {"components": ",".join(map(str, components))}

        # need to call this with a token, since this data is sensitive
        response = await self.api.get_with_token(route=route, params=params)

        # get bungie name
        bungie_name = f"""{response.content["profile"]["data"]["userInfo"]["bungieGlobalDisplayName"]}#{response.content["profile"]["data"]["userInfo"]["bungieGlobalDisplayNameCode"]}"""

        # update name if different
        if bungie_name != self.user.bungie_name:
            await discord_users.update(db=self.db, to_update=self.user, bungie_name=bungie_name)

        return response.content

    async def __get_currency_amount(self, bucket: DestinyInventoryBucketEnum) -> int:
        """Returns the amount of the specified currency owned"""

        profile = await self.__get_profile()
        items = profile["profileCurrencies"]["data"]["items"]

        # get the item with the correct bucket
        value = 0
        for item in items():
            if item["bucketHash"] == bucket.value:
                value = item["quantity"]
        return value
