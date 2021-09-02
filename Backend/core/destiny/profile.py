import dataclasses
import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.destiny.records import records
from Backend.crud.destiny.collectibles import collectibles
from Backend.database.models import Collectibles, DiscordUsers, Records
from Backend.misc.helperFunctions import get_datetime_from_bungie_entry
from Backend.networking.bungieApi import BungieApi
from Backend.networking.BungieRoutes import profile_route, stat_route


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

    async def get_destiny_name(self) -> str:
        """Returns the current user name#1234"""

        result = await self.__get_profile(100)
        user_info = result["profile"]["data"]["userInfo"]
        return f"""{user_info["bungieGlobalDisplayName"]}#{user_info["bungieGlobalDisplayNameCode"]}"""

    async def get_last_online(self) -> datetime.datetime:
        """Returns the last online time"""

        result = await self.__get_profile(100)
        return get_datetime_from_bungie_entry(result["profile"]["data"]["dateLastPlayed"])

    async def has_triumph(self, triumph_hash: str | int) -> bool:
        """Returns if the triumph is gotten"""

        triumph_hash = int(triumph_hash)

        # get from db and return that if it says user got the triumph
        result = await records.has_record(db=self.db, destiny_id=self.destiny_id, triumph_hash=triumph_hash)
        if result:
            return result

        # alright, the user doesn't have the triumph, at least not in the db. So let's update the db entries
        triumphs_data = await self.get_triumphs()
        to_insert = []

        # loop through all triumphs and add them / update them in the db
        for triumph_id, triumph_info in triumphs_data.items():
            triumph_id = int(triumph_id)

            # does the entry exist in the db?
            # we don't need to re calc the state if its already marked as earned in the db
            result = await records.get_record(db=self.db, destiny_id=self.destiny_id, triumph_hash=triumph_id)
            if result and result.completed:
                continue

            # calculate if the triumph is gotten
            status = True
            if "objectives" not in triumph_info:
                # make sure it's RewardUnavailable aka legacy
                assert triumph_info["state"] & 2

                # https://bungie-net.github.io/multi/schema_Destiny-DestinyRecordState.html#schema_Destiny-DestinyRecordState
                status &= triumph_info["state"] & 1

                return status

            for part in triumph_info["objectives"]:
                status &= part["complete"]

            # don't really need to insert not-gained triumphs
            if status:
                # do we need to update or insert?
                if not result:
                    # insert
                    to_insert.append(Records(destiny_id=self.destiny_id, record_id=triumph_id, completed=status))

                else:
                    # update
                    await records.update_record(db=self.db, obj=result, completed=status)

        # mass insert the missing entries
        if to_insert:
            await records.insert_records(db=self.db, objs=to_insert)

        # now check again if it completed
        return await records.has_record(db=self.db, destiny_id=self.destiny_id, triumph_hash=triumph_hash)

    async def has_collectible(self, collectible_hash: str | int) -> bool:
        """Returns if the collectible is gotten"""

        collectible_hash = int(collectible_hash)

        # get from db and return that if it says user got the collectible
        result = await collectibles.has_collectible(
            db=self.db, destiny_id=self.destiny_id, collectible_hash=collectible_hash
        )
        if result:
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
                # do we need to update or insert?
                if not result:
                    # insert
                    to_insert.append(
                        Collectibles(destiny_id=self.destiny_id, collectible_id=collectible_id, owned=status)
                    )

                else:
                    # update
                    await collectibles.update_collectible(db=self.db, obj=result, owned=status)

        # mass insert the missing entries
        if to_insert:
            await collectibles.insert_collectibles(db=self.db, objs=to_insert)

        # now check again if it owned
        return await collectibles.has_collectible(
            db=self.db, destiny_id=self.destiny_id, collectible_hash=collectible_hash
        )

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
    ) -> int:
        """Returns the value of the given stat"""

        possible_stat_categories = [
            "allTime",
            "allPvE",
            "allPvP",
        ]
        assert stat_category in possible_stat_categories, f"Stat must be one of {possible_stat_categories}"

        stats = await self.get_stats()

        # total stats
        if not character_id:
            stat = stats["mergedAllCharacters"]["merged"][stat_category][stat_name]["basic"]["value"]
            return int(stat)

        # character stats
        else:
            for char in stats["characters"]:
                if char["characterId"] == str(character_id):
                    stat = stats["merged"][stat_category][stat_name]["basic"]["value"]
                    return int(stat)

    async def get_artifact(self) -> dict:
        """Returns the seasonal artifact data"""

        result = await self.__get_profile(104, with_token=True)
        return result["profileProgression"]["data"]["seasonalArtifact"]

    async def get_player_seals(self) -> tuple[list[int], list[int]]:
        """Returns all seals and the seals a player has. Returns two lists: [triumph_hash, ...] and removes wip seals like WF LW"""

        all_seals = []
        completed_seals = []

        # todo
        seals = await getSeals()
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
            for character_id, character_data in characters.items():
                if character_data["class"] == character_class:
                    return character_id
        return None

    async def get_character_info(self) -> dict:
        """
        Get character info

        Returns existing_chars=
            {
                charID: {
                    "class": str,
                    "race": str,
                    "gender": str,
                },
                ...
            }
        """

        characters = {}
        result = await self.__get_profile(200)

        # loop through each character
        for characterID, character_data in result["characters"]["data"].items():
            characterID = int(characterID)

            # format the data correctly and convert the hashes to strings
            characters[characterID] = {
                "class": self.class_map[character_data["classHash"]],
                "race": self.race_map[character_data["raceHash"]],
                "gender": self.gender_map[character_data["genderHash"]],
            }

        return characters

    async def get_triumphs(self) -> dict:
        """Populate the triumphs and then return them"""

        result = await self.__get_profile(900)

        # get profile triumphs
        triumphs = result["profileRecords"]["data"]["records"]

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

        result = await self.__get_profile(800)

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

        metrics = await self.__get_profile(1100)
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

        characters = await self.get_character_info()

        # not equipped on characters
        gear = []
        used_items = await self.__get_profile(201, 205, 300, with_token=True)
        item_power = {
            weapon_id: int(weapon_data.get("primaryStat", {"value": 0})["value"])
            for weapon_id, weapon_data in used_items["itemComponents"]["instances"]["data"].items()
        }
        item_power["none"] = 0
        for character_id in characters.keys():
            character_items = (
                used_items["characterInventories"]["data"][character_id]["items"]
                + used_items["characterEquipment"]["data"][character_id]["items"]
            )
            character_power_items = map(
                lambda character_item: dict(
                    character_item,
                    **{"lightlevel": item_power[character_item.get("itemInstanceId", "none")]},
                ),
                character_items,
            )
            gear.extend(character_power_items)

        return gear

    async def __get_profile(self, *components: int | str, with_token: bool = False) -> dict:
        """
        Return info from the profile call
        https://bungie-net.github.io/multi/schema_Destiny-DestinyComponentType.html#schema_Destiny-DestinyComponentType
        """

        route = profile_route.format(system=self.system, destiny_id=self.destiny_id)
        params = {"components": ",".join(map(str, components))}

        if with_token:
            response = await self.api.get_with_token(route=route, params=params)
        else:
            response = await self.api.get(route=route, params=params)

        return response.content
