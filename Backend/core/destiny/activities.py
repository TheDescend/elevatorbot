import dataclasses
import datetime
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.destiny.profile import DestinyProfile
from Backend.database.models import DiscordGuardiansToken
from Backend.networking.bungieApi import BungieApi
from Backend.networking.routes import activities_route, stat_route_characters


@dataclasses.dataclass
class DestinyActivities:
    """API calls focusing on activities"""

    db: AsyncSession
    user: DiscordGuardiansToken

    _full_character_list: list[dict] = dataclasses.field(init=False, default_factory=list)

    def __post_init__(self):
        # some shortcuts
        self.discord_id = self.user.discord_id
        self.destiny_id = self.user.destiny_id
        self.system = self.user.system

        # the network class
        self.api = BungieApi(discord_id=self.discord_id)

    async def get_character_activity_stats(self, character_id: int) -> dict:
        """Get destiny stats for the specified character"""

        route = stat_route_characters.format(system=self.system, destiny_id=self.destiny_id, character_id=character_id)

        result = await self.api.get_json_from_url(route=route)
        return result.content

    async def has_lowman(
        self,
        max_player_count: int,
        activity_hashes: list[int],
        require_flawless: bool = False,
        no_checkpoints: bool = False,
        disallowed: list[tuple[datetime.datetime, datetime.datetime]] = None,
        score_threshold: bool = False,
    ) -> bool:
        """Returns if player has a lowman in the given hashes. Disallowed is a list of (start_time, end_time) with datetime objects"""

        if disallowed is None:
            disallowed = []

        # todo
        low_activity_info = await get_info_on_low_man_activity(
            activity_hashes=activity_hashes,
            player_count=max_player_count,
            destiny_id=self.destiny_id,
            no_checkpoints=no_checkpoints,
            score_threshold=score_threshold,
        )

        for (
            instance_id,
            deaths,
            kills,
            time_played_seconds,
            period,
        ) in low_activity_info:
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
        """Returns tuple[solo_count, solo_is_flawless_count, Optional[solo_fastest]]"""

        solo_count, solo_is_flawless_count, solo_fastest = 0, 0, None

        # todo
        # get player data
        records = await get_info_on_low_man_activity(
            activity_hashes=activity_hashes,
            player_count=1,
            destiny_id=self.destiny_id,
            no_checkpoints=True,
        )

        # prepare player data
        for solo in records:
            solo_count += 1
            if solo["deaths"] == 0:
                solo_is_flawless_count += 1
            if not solo_fastest or (solo["timeplayedseconds"] < solo_fastest):
                solo_fastest = solo["timeplayedseconds"]

        return (
            solo_count,
            solo_is_flawless_count,
            datetime.timedelta(seconds=solo_fastest) if solo_fastest else solo_fastest,
        )

    async def get_activity_history(
        self,
        mode: int = 0,
        earliest_allowed_datetime: datetime.datetime = None,
        latest_allowed_datetime: datetime.datetime = None,
    ) -> AsyncGenerator[Optional[dict]]:
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

        for character in await self.__get_full_character_list():
            character_id = character["char_id"]

            route = activities_route.format(
                system=self.system,
                destiny_id=self.destiny_id,
                character_id=character_id,
            )

            br = False
            page = -1
            while True:
                page += 1

                params = {
                    "mode": mode,
                    "count": 250,
                    "page": page,
                }

                # break once threshold is reached
                if br:
                    break

                # get activities
                rep = await self.api.get_json_from_url(route=route, params=params)

                # break if empty, fe. when pages are over
                if not rep.content:
                    break

                # loop through all activities
                for activity in rep.content["activities"]:
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
                    activity["charid"] = character_id

                    yield activity

    async def __get_full_character_list(self) -> list[dict]:
        """Get all character ids (including deleted characters)"""

        # saving this one is the class to prevent the extra api call should it get called again
        if not self._full_character_list:
            user = DestinyProfile(db=self.db, user=self.user)

            result = await user.get_stats()

            for char in result["characters"]:
                self._full_character_list.append(
                    {
                        "char_id": int(char["characterId"]),
                        "deleted": char["deleted"],
                    }
                )

        return self._full_character_list
