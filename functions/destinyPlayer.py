from __future__ import annotations

import asyncio
import dataclasses
import datetime
import logging
from typing import AsyncGenerator, Optional, Union
from urllib.parse import urljoin

import discord
from discord_slash import SlashContext
from discord_slash.context import InteractionContext

from database.database import lookupDiscordID, lookupSystem, lookupDestinyID, insertFailToGetPgcrInstanceId, \
    getLastUpdated, getPgcrActivity, updateLastUpdated, get_info_on_low_man_activity, getSeals, getWeaponInfo
from functions.dataLoading import get_pgcr, insertPgcrToDB
from functions.formating import embed_message
from networking.bungieAuth import handle_and_return_token
from networking.network import get_json_from_bungie_with_token, get_json_from_url

race_map = {
    2803282938: 'Awoken',
    898834093: 'Exo',
    3887404748: 'Human'
}
gender_map = {
    2204441813: 'Female',
    3111576190: 'Male',
}
class_map = {
    671679327: 'Hunter',
    2271682572: 'Warlock',
    3655393761: 'Titan'
}

dont_know_user_error_message = embed_message(
    f"Error",
    f"I either possess no information about that user or their authentication is outdated. \nPlease `/registerdesc` to fix this issue'"
)


@dataclasses.dataclass(eq=False)
class DestinyPlayer:
    destiny_id: int
    system: int
    discord_id: Optional[int]

    # params that shouldn't be accessed directly
    _characters: dict = dataclasses.field(default_factory=dict)
    _full_character_list: list[dict] = dataclasses.field(default_factory=list)

    _bungie_name: str = None
    _last_played: datetime.datetime = None

    _clan_id: int = None
    _clan_is_online: bool = None

    _triumphs: dict = None
    _collectibles: dict = None
    _metrics: dict = None
    _stats: dict = None
    _character_activity_stats: dict = dataclasses.field(default_factory=dict)

    _seasonal_artifact: dict = None
    _gear: list[dict] = None

    _all_seals: list[int] = dataclasses.field(default_factory=list)
    _completed_seals: list[int] = dataclasses.field(default_factory=list)

    _base_bungie_url: str = "https://stats.bungie.net/Platform/"


    def __eq__(self, other: DestinyPlayer) -> bool:
        return self.destiny_id == other.destiny_id


    @classmethod
    async def from_destiny_id(cls, destiny_id: int, ctx: Union[SlashContext, InteractionContext] = None) -> DestinyPlayer:
        """ Populate with destinyID """

        system = await lookupSystem(destiny_id)
        discord_id = await lookupDiscordID(destiny_id)

        if ctx:
            await ctx.send(hidden=True, embed=dont_know_user_error_message)

        return cls(
            destiny_id=discord_id,
            system=system,
            discord_id=discord_id
        )


    @classmethod
    async def from_discord_id(cls, discord_id: int, ctx: Union[SlashContext, InteractionContext] = None) -> Optional[DestinyPlayer]:
        """ Populate with discordID. Might not work """

        destiny_id = await lookupDestinyID(discord_id)
        if not destiny_id:
            if ctx:
                await ctx.send(hidden=True, embed=dont_know_user_error_message)
            else:
                return None

        system = await lookupSystem(destiny_id)

        return cls(
            destiny_id=discord_id,
            system=system,
            discord_id=discord_id
        )

    async def has_token(self) -> bool:
        """ Returns if the user has a valid token """

        return bool((await handle_and_return_token(self.discord_id)).token)


    async def get_clan_id_and_online_status(self) -> tuple[Optional[int], Optional[bool]]:
        """ Get in-game clan or None """

        url = urljoin(self._base_bungie_url, f"GroupV2/User/{self.system}/{self.destiny_id}/0/1/")
        response = await get_json_from_url(
            url=url
        )
        if response:
            self._clan_id = int(response.content["Response"]["results"][0]["member"]["groupId"])
            self._clan_is_online = response.content["Response"]["results"][0]["member"]["isOnline"]

        return self._clan_id, self._clan_is_online


    def get_discord_user(self, client: discord.Client) -> Optional[discord.User]:
        """ Get discord.User or None """

        return client.get_user(self.discord_id) if self.discord_id else None


    def get_discord_member(self, guild: discord.Guild) -> Optional[discord.Member]:
        """ Get discord.Member for specified guild or None"""

        return guild.get_member(self.discord_id) if self.discord_id else None


    async def has_triumph(self, triumph_hash: str) -> bool:
        """ Returns if the triumph is gotten """

        if not await self.get_triumphs():
            return False
        if triumph_hash not in self._triumphs:
            return False

        # calculate if the triumph is gotten
        status = True
        if "objectives" not in self._triumphs[str(triumph_hash)]:
            # make sure it's RewardUnavailable aka legacy
            assert self._triumphs[triumph_hash]['state'] & 2

            # https://bungie-net.github.io/multi/schema_Destiny-DestinyRecordState.html#schema_Destiny-DestinyRecordState
            status &= (self._triumphs[triumph_hash]['state'] & 1)

            return status

        for part in self._triumphs[triumph_hash]['objectives']:
            status &= part['complete']

        return status


    async def has_collectible(self, collectible_hash: str) -> bool:
        """ Returns if the collectible is gotten """

        if not await self._get_collectibles():
            return False

        # look if its a profile collectible
        if collectible_hash in self._collectibles['profileCollectibles']['data']['collectibles']:
            return self._collectibles['profileCollectibles']['data']['collectibles'][collectible_hash]['state'] & 1 == 0

        # look if its a character specific collectible
        for character_collectibles in self._collectibles['characterCollectibles']['data'].values():
            if collectible_hash in character_collectibles['collectibles']:
                return character_collectibles['collectibles'][collectible_hash]['state'] & 1 == 0

        return False


    async def get_metric_value(self, metric_hash: str) -> Optional[int]:
        """ Returns the value of the given metric hash """

        if not await self._get_collectibles():
            return False

        if metric_hash in self._metrics.keys():
            return self._metrics[metric_hash]["objectiveProgress"]["progress"]
        else:
            return None


    async def get_stat_value(self, stat_name: str, stat_category: str = "allTime", character_id: Union[int, str] = None) -> Optional[int]:
        """ Returns the value of the given stat """

        if not await self._get_stats():
            return None

        possible_stat_categories = [
            "allTime",
            "allPvE",
            "allPvP",
        ]
        assert (stat_category not in possible_stat_categories), f"Stat must be one of {possible_stat_categories}"

        # total stats
        if not character_id:
            try:
                stat = self._stats["mergedAllCharacters"]["merged"][stat_category][stat_name]["basic"]["value"]
                return int(stat)
            except KeyError:
                return None

        # character stats
        else:
            for char in self._stats['characters']:
                if char['characterId'] == str(character_id):
                    try:
                        stat = self._stats["merged"][stat_category][stat_name]["basic"]["value"]
                        return int(stat)
                    except KeyError:
                        return None

        return None


    async def get_artifact(self) -> Optional[dict]:
        """ Returns the seasonal artifact data """

        if not self._seasonal_artifact:
            result = await self._get_profile([104], with_token=True)
            if result:
                self._seasonal_artifact = result['profileProgression']['data']['seasonalArtifact']

        return self._seasonal_artifact


    async def get_player_seals(self) -> tuple[list[int], list[int]]:
        """ Returns all seals and the seals a player has. Returns two lists: [triumph_hash, ...] and removes wip seals like WF LW """

        if not self._all_seals:
            seals = await getSeals()
            for seal in seals:
                self._all_seals.append(seal[0])
                if await self.has_triumph(seal[0]):
                    self._completed_seals.append(seal)

        return self._all_seals, self._completed_seals


    async def get_destiny_name_and_last_played(self) -> tuple[str, datetime.datetime]:
        """ Returns the current user name"""

        if not self._bungie_name:
            result = await self._get_profile([100])
            if result:
                self._bungie_name = result["profile"]["data"]["userInfo"]["displayName"]
                last_played = result["profile"]["data"]["dateLastPlayed"]
                self._last_played = datetime.datetime.strptime(last_played, "%Y-%m-%dT%H:%M:%SZ")

        return self._bungie_name, self._last_played


    async def get_character_info(self) -> Optional[dict]:
        """ Get character info

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

        if not self._characters:
            result = await self._get_profile([200])

            if result:
                self._characters = {}

                # loop through each character
                for characterID, character_data in result['characters']['data'].items():
                    characterID = int(characterID)

                    # format the data correctly and convert the hashes to strings
                    self._characters[characterID] = {
                        "class": class_map[character_data["classHash"]],
                        "race": race_map[character_data["raceHash"]],
                        "gender": gender_map[character_data["genderHash"]]
                    }

        return self._characters


    async def get_character_id_by_class(self, character_class: str) -> Optional[int]:
        """ Return the matching character id if exists """

        # make sure the class exists
        class_names = list(class_map.values())
        if character_class not in class_names:
            return None

        # loop through the chars and return the matching one
        characters = await self.get_character_info()
        if characters:
            for character_id, character_data in characters.items():
                if character_data["class"] == character_class:
                    return character_id
        return None


    async def get_character_activity_stats(self, character_id: int) -> Optional[dict]:
        """ Get destiny stats for the specified character """

        if character_id not in self._character_activity_stats:
            url = urljoin(self._base_bungie_url, f"Destiny2/{self.system}/Account/{self.destiny_id}/Character/{character_id}/Stats/AggregateActivityStats/")
            response = await get_json_from_url(
                url=url
            )
            if response:
                self._character_activity_stats[character_id] = response.content['Response']

        return self._character_activity_stats[character_id] if character_id in self._character_activity_stats else None


    async def get_player_gear(self) -> Optional[list[dict]]:
        """ Returns a list of items - equipped and unequipped """

        if not self._gear:
            characters = await self.get_character_info()

            # not equipped on characters
            used_items = await self._get_profile([201, 205, 300], with_token=True)
            if used_items:
                item_power = {
                    weapon_id: int(weapon_data.get("primaryStat", {"value": 0})['value'])
                    for weapon_id, weapon_data in used_items["itemComponents"]["instances"]["data"].items()
                }
                item_power['none'] = 0
                for character_id in characters.keys():
                    character_items = used_items["characterInventories"]["data"][character_id]["items"] + used_items['characterEquipment']["data"][character_id]["items"]
                    character_power_items = map(
                        lambda character_item: dict(character_item, **{'lightlevel': item_power[character_item.get('itemInstanceId', 'none')]}),
                        character_items)
                    self._gear.extend(character_power_items)

        return self._gear


    async def get_weapon_stats(self, weapon_ids: list[int], character_id: int = None, mode: int = 0) -> tuple[int, int]:
        """ Returns kills, precision_kills for that weapon in the specified mode """

        # get the info from the DB
        results = []
        for weapon_id in weapon_ids:
            if character_id:
                results.extend(await getWeaponInfo(
                    membershipID=self.destiny_id,
                    weaponID=weapon_id,
                    characterID=character_id,
                    mode=mode
                ))
            else:
                results.extend(await getWeaponInfo(
                    membershipID=self.destiny_id,
                    weaponID=weapon_id,
                    mode=mode
                ))

        # add stats
        kills = 0
        precision_kills = 0
        for _, k, p_k in results:
            kills += k
            precision_kills += p_k

        return kills, precision_kills


    async def has_lowman(self, max_player_count: int, activity_hashes: list[int], require_flawless: bool = False, no_checkpoints: bool = False, disallowed: list[tuple[datetime.datetime, datetime.datetime]] = None, score_threshold: bool = False) -> bool:
        """ Returns if player has a lowman in the given hashes. Disallowed is a list of (start_time, end_time) with datetime objects """

        if disallowed is None:
            disallowed = []

        low_activity_info = await get_info_on_low_man_activity(
            activity_hashes=activity_hashes,
            player_count=max_player_count,
            destiny_id=self.destiny_id,
            no_checkpoints=no_checkpoints,
            score_threshold=score_threshold,
        )

        for (instance_id, deaths, kills, time_played_seconds, period) in low_activity_info:
            # check for flawless if asked for
            if not require_flawless or deaths == 0:
                verdict = True

                for start_time, end_time in disallowed:
                    if start_time < period < end_time:
                        verdict = False
                if 910380154 in activity_hashes and kills * 60 / time_played_seconds < 1:
                    verdict = False
                if verdict:
                    return True
        return False


    async def get_lowman_count(self, activity_hashes: list[int]) -> tuple[int, int, Optional[datetime.timedelta]]:
        """ Returns tuple[solo_count, solo_is_flawless_count, Optional[solo_fastest]] """

        solo_count, solo_is_flawless_count, solo_fastest = 0, 0, None

        # get player data
        records = await get_info_on_low_man_activity(
            activity_hashes=activity_hashes,
            player_count=1,
            destiny_id=self.destiny_id,
            no_checkpoints=True
        )

        # prepare player data
        for solo in records:
            solo_count += 1
            if solo["deaths"] == 0:
                solo_is_flawless_count += 1
            if not solo_fastest or (solo["timeplayedseconds"] < solo_fastest):
                solo_fastest = solo["timeplayedseconds"]

        return solo_count, solo_is_flawless_count, datetime.timedelta(seconds=solo_fastest) if solo_fastest else solo_fastest


    async def get_activity_history(self, mode: int = 0, earliest_allowed_datetime: datetime.datetime = None, latest_allowed_datetime: datetime.datetime = None) -> AsyncGenerator[dict]:
        """
        Generator which returns all activities with an extra field < activity['charid'] = character_id >
        For more Info visit https://bungie-net.github.io/multi/schema_Destiny-HistoricalStats-DestinyHistoricalStatsPeriodGroup.html#schema_Destiny-HistoricalStats-DestinyHistoricalStatsPeriodGroup

        :mode - Describes the mode, see https://bungie-net.github.io/multi/schema_Destiny-HistoricalStats-Definitions-DestinyActivityModeType.html#schema_Destiny-HistoricalStats-Definitions-DestinyActivityModeType
            Everything	0
            Story	    2
            Strike	    3
            Raid	    4
            AllPvP	    5
            Patrol	    6
            AllPvE	    7
            ...
        :earliest_allowed_time - takes datetime.datetime and describes the lower cutoff
        :latest_allowed_time - takes datetime.datetime and describes the higher cutoff
        """

        for character in await self._get_full_character_list():
            character_id = character["char_id"]

            br = False
            page = -1
            while True:
                page += 1

                url = urljoin(self._base_bungie_url, f"Destiny2/{self.system}/Account/{self.destiny_id}/Character/{character_id}/Stats/Activities/")
                params = {
                    "mode": mode,
                    "count": 250,
                    "page": page,
                }

                # break once threshold is reached
                if br:
                    break

                # get activities
                rep = await get_json_from_url(
                    url=url,
                    params=params
                )

                # break if empty, fe. when pages are over
                if not rep.content:
                    break

                # loop through all activities
                for activity in rep.content['Response']['activities']:
                    # check times if wanted
                    if earliest_allowed_datetime or latest_allowed_datetime:
                        activity_time = datetime.datetime.strptime(activity["period"], "%Y-%m-%dT%H:%M:%SZ")

                        # check if the activity started later than the earliest allowed, else break and continue with next char
                        # This works bc Bungie sorts the api with the newest entry on top
                        if earliest_allowed_datetime:
                            if activity_time <= earliest_allowed_datetime:
                                br = True
                                break

                        # check if the time is still in the timeframe, else pass this one and do the next
                        if latest_allowed_datetime:
                            if activity_time > latest_allowed_datetime:
                                pass

                    # add character info to the activity
                    activity['charid'] = character_id

                    yield activity


    async def update_activity_db(self, entry_time: datetime = None) -> None:
        """ Gets this users not-saved history and saves it """

        async def handle(i: int, t) -> Optional[list[int, datetime.datetime, dict]]:
            # get PGCR
            pgcr = await get_pgcr(i)
            if not pgcr:
                await insertFailToGetPgcrInstanceId(i, t)
                logger.warning('Failed getting pgcr <%s>', i)
                return
            return [i, t, pgcr.content["Response"]]


        async def input_data(gather_instance_ids: list[int], gather_activity_times: list[datetime.datetime]) -> None:
            results = await asyncio.gather(*[
                handle(i, t)
                for i, t in zip(gather_instance_ids, gather_activity_times)
            ])

            for result in results:
                if result:
                    i = result[0]
                    t = result[1]
                    pgcr = result[2]

                    # insert information to DB
                    await insertPgcrToDB(i, t, pgcr)

        logger = logging.getLogger('update_activity_db')

        if not entry_time:
            entry_time = await getLastUpdated(self.destiny_id)
        else:
            entry_time = datetime.datetime.min

        logger.info('Starting activity DB update for destinyID <%s>', self.destiny_id)

        instance_ids = []
        activity_times = []
        async for activity in self.get_activity_history(
            mode=0,
            earliest_allowed_datetime=entry_time,
        ):
            instance_id = activity["activityDetails"]["instanceId"]
            activity_time = datetime.datetime.strptime(activity["period"], "%Y-%m-%dT%H:%M:%SZ")

            # update with newest entry timestamp
            if activity_time > entry_time:
                entry_time = activity_time

            # check if info is already in DB, skip if so
            if await getPgcrActivity(instance_id):
                continue

            # add to gather list
            instance_ids.append(instance_id)
            activity_times.append(activity_time)

            # gather once list is big enough
            if len(instance_ids) < 50:
                continue
            else:
                # get and input the data
                await input_data(instance_ids, activity_times)

                # reset gather list and restart
                instance_ids = []
                activity_times = []

        # one last time to clean out the extras after the code is done
        if instance_ids:
            # get and input the data
            await input_data(instance_ids, activity_times)

        # update with newest entry timestamp
        await updateLastUpdated(self.destiny_id, entry_time)

        logger.info('Done with activity DB update for destinyID <%s>', self.destiny_id)


    async def _get_full_character_list(self) -> list[dict]:
        """ Get character ids including deleted characters """

        if not self._full_character_list:
            result = self._get_stats()

            if result:
                for char in result["characters"]:
                    self._full_character_list.append({
                        "char_id": int(char["characterId"]),
                        "deleted": char["deleted"],
                    })

        return self._full_character_list


    async def _get_profile(self, components: list[Union[int, str]] = None, with_token: bool = False) -> Optional[dict]:
        """ Return info from the profile call """

        # https://bungie-net.github.io/multi/schema_Destiny-DestinyComponentType.html#schema_Destiny-DestinyComponentType

        if components is None:
            components = []

        url = urljoin(self._base_bungie_url, f"Destiny2/{self.system}/Profile/{self.destiny_id}/")
        params = {
            "components": ",".join(map(str, components))
        }

        if with_token:
            response = await get_json_from_bungie_with_token(
                url=url,
                params=params,
                discord_id=self.discord_id
            )
        else:
            response = await get_json_from_url(
                url=url,
                params=params,
            )

        return response.content['Response'] if response else None


    async def get_triumphs(self) -> Optional[dict]:
        """ Populate the triumphs and then return them """

        if not self._triumphs:
            triumphs = await self._get_profile([900])
            if triumphs:
                # get profile triumphs
                self._triumphs = triumphs['profileRecords']['data']['records']

                # get character triumphs
                character_triumphs = [character_triumphs['records'] for character_id, character_triumphs in triumphs['characterRecords']['data'].items()]

                # combine them
                for triumph in character_triumphs:
                    self._triumphs.update(triumph)

        return self._triumphs


    async def _get_collectibles(self) -> Optional[dict]:
        """ Populate the collectibles and then return them """

        if not self._collectibles:
            collectibles = await self._get_profile([800])
            if collectibles:
                # get profile collectibles
                self._collectibles = collectibles

        return self._collectibles


    async def _get_metrics(self) -> Optional[dict]:
        """ Populate the metrics and then return them """

        if not self._metrics:
            metrics = await self._get_profile([1100])
            if metrics:
                # get profile metrics
                self._metrics = metrics["metrics"]["data"]['metrics']

        return self._metrics


    async def _get_stats(self) -> Optional[dict]:
        """ Get destiny stats """

        if not self._stats:
            url = urljoin(self._base_bungie_url, f"Destiny2/{self.system}/Account/{self.destiny_id}/Stats/")
            response = await get_json_from_url(
                url=url
            )
            if response:
                self._stats = response.content['Response']

        return self._stats


    async def get_inventory_bucket(self, bucket: int = 138197802) -> Optional[list]:
        """ Returns all items in bucket. Default is vault hash, for others search "bucket" at https://data.destinysets.com/"""

        result = await self._get_profile([102], with_token=True)
        if not result:
            return None
        all_items = result["profileInventory"]["data"]["items"]
        items = []
        for item in all_items:
            if item["bucketHash"] == bucket:
                items.append(item)

        return items
