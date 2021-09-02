import asyncio
import dataclasses
import datetime
import logging
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.destiny.profile import DestinyProfile
from Backend.core.errors import CustomException
from Backend.crud import activities, activities_fail_to_get, discord_users
from Backend.database.models import ActivitiesFailToGet, DiscordUsers
from Backend.misc.helperFunctions import get_datetime_from_bungie_entry
from Backend.networking.bungieApi import BungieApi
from Backend.networking.BungieRoutes import activities_route, pgcr_route, stat_route_characters
from Backend.networking.schemas import WebResponse


@dataclasses.dataclass
class DestinyActivities:
    """API calls focusing on activities"""

    db: AsyncSession
    user: DiscordUsers

    _full_character_list: list[dict] = dataclasses.field(init=False, default_factory=list)

    def __post_init__(self):
        # some shortcuts
        self.discord_id = self.user.discord_id
        self.destiny_id = self.user.destiny_id
        self.system = self.user.system

        # the network class
        self.api = BungieApi(db=self.db, user=self.user)

    async def get_character_activity_stats(self, character_id: int) -> dict:
        """Get destiny stats for the specified character"""

        route = stat_route_characters.format(system=self.system, destiny_id=self.destiny_id, character_id=character_id)

        result = await self.api.get(route=route)
        return result.content

    async def has_lowman(
        self,
        max_player_count: int,
        activity_hashes: list[int],
        require_flawless: bool = False,
        no_checkpoints: bool = False,
        disallowed_datetimes: list[tuple[datetime.datetime, datetime.datetime]] = None,
        score_threshold: int = None,
        min_kills_per_minute: float = None
    ) -> bool:
        """Returns if player has a lowman in the given hashes. Disallowed is a list of (start_time, end_time) with datetime objects"""

        low_activity_info = await activities.get_low_man_activities(
            db=self.db,
            activity_hashes=activity_hashes,
            player_count=max_player_count,
            destiny_id=self.destiny_id,
            no_checkpoints=no_checkpoints,
            score_threshold=score_threshold,
            require_flawless=require_flawless,
            min_kills_per_minute=min_kills_per_minute,
            disallowed_datetimes=disallowed_datetimes,
        )
        return bool(low_activity_info)


    async def get_lowman_count(
        self,
        activity_hashes: list[int],
        max_player_count: int,
        require_flawless: bool = False,
        no_checkpoints: bool = False,
        disallowed_datetimes: list[tuple[datetime.datetime, datetime.datetime]] = None,
        score_threshold: int = None,
        min_kills_per_minute: float = None
    ) -> tuple[int, int, Optional[datetime.timedelta]]:
        """Returns tuple[solo_count, solo_is_flawless_count, Optional[solo_fastest]]"""

        solo_count, solo_is_flawless_count, solo_fastest = 0, 0, None

        # get player data
        low_activity_info = await activities.get_low_man_activities(
            db=self.db,
            activity_hashes=activity_hashes,
            player_count=max_player_count,
            destiny_id=self.destiny_id,
            no_checkpoints=no_checkpoints,
            score_threshold=score_threshold,
            require_flawless=require_flawless,
            min_kills_per_minute=min_kills_per_minute,
            disallowed_datetimes=disallowed_datetimes,
        )

        # prepare player data
        # todo get and process data. No idea how it actually looks tbh. Need changing!
        for solo in low_activity_info:
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
    ) -> AsyncGenerator[dict]:
        """
        Generator which returns all activities with an extra field < activity['character_id'] = character_id >
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
                rep = await self.api.get(route=route, params=params)

                # break if empty, fe. when pages are over
                if not rep.content:
                    break

                # loop through all activities
                for activity in rep.content["activities"]:
                    # also update the period entry to be datetime instead of the string representation
                    activity_time = get_datetime_from_bungie_entry(activity["period"])
                    activity["period"] = activity_time

                    # check times if wanted
                    if earliest_allowed_datetime or latest_allowed_datetime:
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
                    activity["character_id"] = character_id

                    yield activity


    async def update_missing_pgcr(
        self
    ):
        """Insert the missing pgcr"""

        for activity in await activities_fail_to_get.get_all():
            # check if info is already in DB, delete and skip if so
            result = activity.get(db=self.db, instance_id=activity.instance_id)
            if result:
                await activities_fail_to_get.delete(db=self.db, obj=activity)
                continue

            # get PGCR
            try:
                pgcr = await self.get_pgcr(instance_id=activity.instance_id)

            except CustomException:
                # only continue if we get a response this time
                continue

            # add info to DB
            await activities.insert(db=self.db, instance_id=activity.instance_id, activity_time=activity.period, pgcr=pgcr.content)

            # delete from to-do DB
            await activities_fail_to_get.delete(db=self.db, obj=activity)

    async def get_pgcr(self, instance_id: int) -> WebResponse:
        """Return the pgcr from the api"""

        return await self.api.get(route=pgcr_route.format(instance_id=instance_id))

    async def update_activity_db(self, entry_time: datetime = None):
        """Gets this users not-saved history and saves it in the db"""

        async def handle(i: int, t: datetime.datetime) -> Optional[list[int, datetime.datetime, dict]]:
            """Get pgcr"""

            try:
                pgcr = await self.get_pgcr(i)

            except CustomException:
                # looks like it failed, lets try again later
                logger.warning("Failed getting pgcr <%s>", i)
                await activities_fail_to_get.insert(db=self.db, instance_id=i, period=t)

                return
            return [i, t, pgcr.content]

        async def input_data(gather_instance_ids: list[int], gather_activity_times: list[datetime.datetime]):
            """Gather all pgcr and insert them"""

            results = await asyncio.gather(*[handle(i, t) for i, t in zip(gather_instance_ids, gather_activity_times)])

            for result in results:
                if result:
                    i = result[0]
                    t = result[1]
                    pgcr = result[2]

                    # insert information to DB
                    await activities.insert(db=self.db, instance_id=i, activity_time=t, pgcr=pgcr)

        # get the logger
        logger = logging.getLogger("update_activity_db")

        # get the entry time
        if not entry_time:
            entry_time = self.user.activities_last_updated

        logger.info("Starting activity DB update for destinyID <%s>", self.destiny_id)

        # loop through all activities
        instance_ids = []
        activity_times = []
        success = False
        async for activity in self.get_activity_history(mode=0, earliest_allowed_datetime=entry_time):
            success = True

            instance_id: int = activity["activityDetails"]["instanceId"]
            activity_time: datetime.datetime = activity["period"]

            # _update with newest entry timestamp
            if activity_time > entry_time:
                entry_time = activity_time

            # check if info is already in DB, skip if so
            if await activities.get(db=self.db, instance_id=instance_id) is not None:
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
        if success:
            await discord_users.update(db=self.db, to_update=self.user, activities_last_updated=entry_time)

        logger.info("Done with activity DB update for destinyID <%s>", self.destiny_id)

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
