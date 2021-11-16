import asyncio
import dataclasses
import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud import activities, destiny_manifest, discord_users
from Backend.crud.cache import cache
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
from Backend.misc.helperFunctions import get_datetime_from_bungie_entry
from Backend.networking.bungieApi import BungieApi
from Backend.networking.bungieRoutes import profile_route, stat_route
from DestinyEnums.enums import DestinyInventoryBucketEnum
from NetworkingSchemas.basic import ValueModel
from NetworkingSchemas.destiny.account import (
    BoolModelObjective,
    BoolModelRecord,
    DestinyCharacterModel,
    DestinyCharactersModel,
    DestinyTriumphScoreModel,
    SeasonalChallengesModel,
    SeasonalChallengesRecordModel,
    SeasonalChallengesTopicsModel,
)


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

    def __post_init__(self):
        # some shortcuts
        self.discord_id = self.user.discord_id
        self.destiny_id = self.user.destiny_id
        self.system = self.user.system

        # the network class
        self.api = BungieApi(db=self.db, user=self.user)

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
                    triumph_id = int(triumph_id)

                    # does the entry exist in the db?
                    # we don't need to re calc the state if its already marked as earned in the db
                    result = await records.get_record(db=self.db, destiny_id=self.destiny_id, triumph_hash=triumph_id)
                    if result and result.completed:
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
                            to_insert.append(Records(destiny_id=self.destiny_id, record_id=triumph_id, completed=True))

                        else:
                            # update
                            await records.update_record(db=self.db, obj=result, completed=True)

                # mass insert the missing entries
                if to_insert:
                    await records.insert_records(db=self.db, objs=to_insert)

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
                # get from db and return that if it says user got the collectible
                result = await collectibles.has_collectible(
                    db=self.db, destiny_id=self.destiny_id, collectible_hash=collectible_hash
                )
                if result:
                    # only caching already got collectibles
                    cache.collectibles[self.destiny_id].update({collectible_hash: True})
                    return result

                # as with the triumphs, we need to update our local collectible data now
                collectibles_data = await self.get_collectibles()
                to_insert = []

                # loop through the collectibles
                for collectible_id, collectible_info in collectibles_data.items():
                    collectible_id = int(collectible_id)

                    # does the entry exist in the db?
                    # we don't need to re calc the state if its already marked as owned in the db
                    result = await collectibles.get_collectible(
                        db=self.db, destiny_id=self.destiny_id, collectible_hash=collectible_id
                    )
                    if result and result.owned:
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

        # now check again if its owned
        if collectible_hash in cache.collectibles[self.destiny_id]:
            return True
        else:
            return False

    async def get_metric_value(self, metric_hash: str | int) -> int:
        """Returns the value of the given metric hash"""

        metric_hash = str(metric_hash)
        metrics = await self.get_metrics()

        return metrics[metric_hash]["objectiveProgress"]["progress"]

    async def get_stat_value(
        self,
        stat_name: str,
        stat_category: str = "allTime",
        character_id: int | str = None,
    ) -> int | float:
        """Returns the value of the given stat. Int if no decimals, else float"""

        possible_stat_categories = [
            "allTime",
            "allPvE",
            "allPvP",
        ]
        assert stat_category in possible_stat_categories, f"Stat must be one of {possible_stat_categories}"

        stats = await self.get_stats()

        # total stats
        if not character_id:
            stat: float = stats["mergedAllCharacters"]["merged"][stat_category][stat_name]["basic"]["value"]
            return int(stat) if stat.is_integer() else stat

        # character stats
        else:
            for char in stats["characters"]:
                if char["characterId"] == str(character_id):
                    stat: float = stats["merged"][stat_category][stat_name]["basic"]["value"]
                    return int(stat) if stat.is_integer() else stat

    async def get_artifact_level(self) -> ValueModel:
        """Returns the seasonal artifact data"""

        result = await self.__get_profile(104, with_token=True)
        return ValueModel(value=result["profileProgression"]["data"]["seasonalArtifact"]["powerBonus"])

    async def get_season_pass_level(self) -> ValueModel:
        """Returns the seasonal pass level"""

        # get the current season pass hash
        async with asyncio.Lock():
            if not cache.season_pass_definition:
                cache.season_pass_definition = await destiny_manifest.get_current_season_pass(db=self.db)

        # get a character id since they are character specific
        character_id = (await self.get_character_ids())[0]

        result = await self.__get_profile(202, with_token=True)
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
                bar_length = 10
                bar_text = ""
                for i in range(bar_length):
                    if round(percentage, 1) <= 1 / bar_length * i:
                        bar_text += "░"
                    else:
                        bar_text += "▓"

                sc.completion_percentage = percentage
                sc.completion_status = bar_text

        return user_sc

    async def get_player_seals(self) -> tuple[list[int], list[int]]:
        """Returns all seals and the seals a player has. Returns two lists: [triumph_hash, ...] and removes wip seals like WF LW"""

        all_seals = []
        completed_seals = []

        seals = await destiny_manifest.get_seals(db=self.db)
        for seal in seals:
            all_seals.append(seal[0])
            if await self.has_triumph(seal[0]):
                completed_seals.append(seal)

        return all_seals, completed_seals

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

        return triumphs

    async def get_collectibles(self) -> dict:
        """Populate the collectibles and then return them"""

        result = await self.__get_profile()

        # get profile triumphs
        collectibles = result["profileCollectibles"]["data"]["collectibles"]

        # get character triumphs
        character_collectibles = [
            character_triumphs["collectibles"]
            for _, character_triumphs in result["characterCollectibles"]["data"].items()
        ]

        # combine them
        for character in character_collectibles:
            # loop through all the collectibles and only update them if the collectible is earned
            # see https://bungie-net.github.io/multi/schema_Destiny-DestinyCollectibleState.html#schema_Destiny-DestinyCollectibleState
            for collectible_hash, collectible_state in character:
                if collectible_state["state"] & 1 == 0:
                    collectibles.update({collectible_hash: collectible_state})

        return collectibles

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

        result = await self.__get_profile(102, with_token=True)
        all_items = result["profileInventory"]["data"]["items"]
        items = []
        for item in all_items:
            if item["bucketHash"] == bucket:
                items.append(item)

        return items

    async def get_player_gear(self) -> list[dict]:
        """Returns a list of items - equipped and unequipped"""

        characters = await self.get_character_ids()

        # not equipped on characters
        gear = []
        used_items = await self.__get_profile(201, 205, 300, with_token=True)
        item_power = {
            weapon_id: int(weapon_data._get("primaryStat", {"value": 0})["value"])
            for weapon_id, weapon_data in used_items["itemComponents"]["instances"]["data"].items()
        }
        item_power["none"] = 0
        for character_id in characters:
            character_items = (
                used_items["characterInventories"]["data"][character_id]["items"]
                + used_items["characterEquipment"]["data"][character_id]["items"]
            )
            character_power_items = map(
                lambda character_item: dict(
                    character_item,
                    **{"lightlevel": item_power[character_item._get("itemInstanceId", "none")]},
                ),
                character_items,
            )
            gear.extend(character_power_items)

        return gear

    async def get_time_played(
        self,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        mode: int = 0,
        activity_ids: Optional[list[int]] = None,
        character_class: Optional[str] = None,
    ) -> int:
        """Get the time played (in seconds)"""

        return await activities.calculate_time_played(
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

        result = await self.__get_profile(102, with_token=True)

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
        self, *buckets: DestinyInventoryBucketEnum, include_item_level: bool = False
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

        components = [102]
        if include_item_level:
            components.append(300)
        result = await self.__get_profile(*components, with_token=True)

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

        class_to_unlock_hash = {
            2166136261, # Hunter
        }

        # default is vault
        if not buckets:
            buckets = DestinyInventoryBucketEnum.all

        components = [102, 200, 201, 205]
        if include_item_level:
            components.append(300)
        result = await self.__get_profile(*components, with_token=True)
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
            if profile_data["bucketHash"] == DestinyInventoryBucketEnum.VAULT.value and "itemInstanceId" in profile_data:
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
                                    "power_level": result["itemComponents"]["instances"]["data"][str(profile_data["itemHash"])][
                                        "primaryStat"
                                    ]["value"]
                                }
                            )
                        except KeyError:
                            pass

        return items

    async def __get_profile(self, *components_override: int, with_token: bool = False) -> dict:
        """
        Return info from the profile call
        https://bungie-net.github.io/multi/schema_Destiny-DestinyComponentType.html#schema_Destiny-DestinyComponentType

        Call the override if you want specific components, otherwise its always the default
        Default: components_override = (100, 200, 800, 900, 1100)
        """

        if not components_override:
            components_override = (100, 200, 800, 900, 1100)

        # add 100 to the profile call. Remove that data in the result and only use it to update Bungie Name
        added = False
        if 100 not in components_override:
            added = True
            components_override += (100,)

        route = profile_route.format(system=self.system, destiny_id=self.destiny_id)
        params = {"components": ",".join(map(str, components_override))}

        if with_token:
            response = await self.api.get_with_token(route=route, params=params)
        else:
            response = await self.api.get(route=route, params=params)

        # get bungie name
        bungie_name = f"""{response.content["profile"]["data"]["userInfo"]["bungieGlobalDisplayName"]}#{response.content["profile"]["data"]["userInfo"]["bungieGlobalDisplayNameCode"]}"""

        # update name if different
        if bungie_name != self.user.bungie_name:
            await discord_users.update(db=self.db, to_update=self.user, bungie_name=bungie_name)

        # remove 100 data from response
        if added:
            response.content.pop("profile")

        return response.content
