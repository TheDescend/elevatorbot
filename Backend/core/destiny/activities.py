import asyncio
import dataclasses
import datetime
import logging
from collections.abc import AsyncGenerator
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.destiny.profile import DestinyProfile
from Backend.core.errors import CustomException
from Backend.crud import activities, activities_fail_to_get, discord_users
from Backend.database.models import DiscordUsers
from Backend.misc.helperFunctions import get_datetime_from_bungie_entry
from Backend.networking.bungieApi import BungieApi
from Backend.networking.bungieRoutes import (
    activities_route,
    pgcr_route,
    stat_route_characters,
)
from Backend.networking.schemas import WebResponse
from Backend.schemas.destiny.activities import DestinyLowManModel


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

    async def get_lowman_count(
        self,
        activity_ids: list[int],
        max_player_count: int,
        require_flawless: bool = False,
        no_checkpoints: bool = True,
        disallowed_datetimes: list[tuple[datetime.datetime, datetime.datetime]] = None,
        score_threshold: int = None,
        min_kills_per_minute: float = None,
    ) -> DestinyLowManModel:
        """Returns low man data"""

        count, flawless_count, not_flawless_count, fastest = 0, 0, 0, None

        # _get player data
        low_activity_info = await activities.get_activities(
            db=self.db,
            activity_hashes=activity_ids,
            maximum_allowed_players=max_player_count,
            destiny_id=self.destiny_id,
            no_checkpoints=no_checkpoints,
            require_score=score_threshold,
            require_team_flawless=require_flawless,
            require_kills_per_minute=min_kills_per_minute,
            disallow_time_periods=disallowed_datetimes,
        )

        # prepare player data
        # todo _get and process data. No idea how it actually looks tbh. Need changing!
        for solo in low_activity_info:
            count += 1
            if solo["deaths"] == 0:
                flawless_count += 1
            else:
                not_flawless_count += 1
            if not fastest or (solo["timeplayedseconds"] < fastest):
                fastest = datetime.timedelta(seconds=solo["timeplayedseconds"])

        return DestinyLowManModel(
            activity_ids=activity_ids,
            count=count,
            flawless_count=flawless_count,
            not_flawless_count=not_flawless_count,
            fastest=fastest,
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

                # _get activities
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

    async def update_missing_pgcr(self):
        """Insert the missing pgcr"""

        for activity in await activities_fail_to_get.get_all():
            # check if info is already in DB, delete and skip if so
            result = activity._get(db=self.db, instance_id=activity.instance_id)
            if result:
                await activities_fail_to_get.delete(db=self.db, obj=activity)
                continue

            # _get PGCR
            try:
                pgcr = await self.get_pgcr(instance_id=activity.instance_id)

            except CustomException:
                # only continue if we _get a response this time
                continue

            # add info to DB
            await activities.insert(
                db=self.db, instance_id=activity.instance_id, activity_time=activity.period, pgcr=pgcr.content
            )

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

        # _get the logger
        logger = logging.getLogger("updateActivityDb")

        # _get the entry time
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
            if await activities._get(db=self.db, instance_id=instance_id) is not None:
                continue

            # add to gather list
            instance_ids.append(instance_id)
            activity_times.append(activity_time)

            # gather once list is big enough
            if len(instance_ids) < 50:
                continue
            else:
                # _get and input the data
                await input_data(instance_ids, activity_times)

                # reset gather list and restart
                instance_ids = []
                activity_times = []

        # one last time to clean out the extras after the code is done
        if instance_ids:
            # _get and input the data
            await input_data(instance_ids, activity_times)

        # update with newest entry timestamp
        if success:
            await discord_users.update(db=self.db, to_update=self.user, activities_last_updated=entry_time)

        logger.info("Done with activity DB update for destinyID <%s>", self.destiny_id)

    async def __get_full_character_list(self) -> list[dict]:
        """Get all character ids (including deleted characters)"""

        # saving this one is the class to prevent the extra api call should it _get called again
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
