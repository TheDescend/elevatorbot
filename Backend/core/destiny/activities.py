import asyncio
import dataclasses
import datetime
import logging
from collections.abc import AsyncGenerator
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.destiny.profile import DestinyProfile
from Backend.core.errors import CustomException
from Backend.crud import (
    crud_activities,
    crud_activities_fail_to_get,
    destiny_manifest,
    discord_users,
)
from Backend.database.base import get_async_session
from Backend.database.models import ActivitiesUsers, DiscordUsers
from Backend.misc.cache import cache
from Backend.misc.helperFunctions import get_datetime_from_bungie_entry, get_now_with_tz
from Backend.networking.bungieApi import BungieApi
from Backend.networking.bungieRoutes import activities_route, pgcr_route
from Backend.networking.schemas import WebResponse
from NetworkingSchemas.destiny.account import (
    DestinyLowMansModel,
    DestinyUpdatedLowManModel,
)
from NetworkingSchemas.destiny.activities import (
    DestinyActivityDetailsModel,
    DestinyActivityDetailsUsersModel,
    DestinyActivityOutputModel,
    DestinyLowManModel,
)
from NetworkingSchemas.destiny.roles import TimePeriodModel


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

    async def get_lowman_count(
        self,
        activity_ids: list[int],
        max_player_count: int,
        require_flawless: bool = False,
        no_checkpoints: bool = True,
        disallowed_datetimes: Optional[list[TimePeriodModel]] = None,
        score_threshold: Optional[int] = None,
        min_kills_per_minute: Optional[float] = None,
    ) -> DestinyLowManModel:
        """Returns low man data"""

        count, flawless_count, not_flawless_count, fastest = 0, 0, 0, None

        # get player data
        low_activity_info = await crud_activities.get_activities(
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
        for solo in low_activity_info:
            count += 1
            if solo.deaths == 0:
                flawless_count += 1
            else:
                not_flawless_count += 1
            if not fastest or (solo.time_played_seconds < fastest):
                fastest = datetime.timedelta(seconds=solo.time_played_seconds)

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
        earliest_allowed_datetime: Optional[datetime.datetime] = None,
        latest_allowed_datetime: Optional[datetime.datetime] = None,
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

    async def update_missing_pgcr(self):
        """Insert the missing pgcr"""

        async with asyncio.Lock():
            for activity in await crud_activities_fail_to_get.get_all_name():
                # check if info is already in DB, delete and skip if so
                result = crud_activities.get(db=self.db, instance_id=activity.instance_id)
                if result:
                    await crud_activities_fail_to_get.delete(db=self.db, obj=activity)
                    continue

                # get PGCR
                try:
                    pgcr = await self.get_pgcr(instance_id=activity.instance_id)

                except CustomException:
                    # only continue if we get a response this time
                    continue

                # add info to DB
                await crud_activities.insert(
                    db=self.db, instance_id=activity.instance_id, activity_time=activity.period, pgcr=pgcr.content
                )

                # delete from to-do DB
                await crud_activities_fail_to_get.delete(db=self.db, obj=activity)
                cache.saved_pgcrs.add(activity.instance_id)

    async def get_pgcr(self, instance_id: int) -> WebResponse:
        """Return the pgcr from the api"""

        return await self.api.get(route=pgcr_route.format(instance_id=instance_id))

    async def get_last_played(
        self,
        mode: int = 0,
        activity_ids: Optional[list[int]] = None,
        character_class: Optional[str] = None,
        completed: bool = True,
    ) -> DestinyActivityDetailsModel:
        """Get the last activity played"""

        result = await crud_activities.get_last_activity(
            db=self.db,
            destiny_id=self.destiny_id,
            mode=mode,
            activity_ids=activity_ids,
            completed=completed,
            character_class=character_class,
        )
        if not result:
            raise CustomException("NoActivityFound")

        # format that
        data = DestinyActivityDetailsModel(
            instance_id=result.instance_id,
            period=result.period,
            starting_phase_index=result.starting_phase_index,
            reference_id=result.reference_id,
            activity_duration_seconds=0,  # temp value
            score=0,  # temp value
        )

        # loop through the users
        for user in result.users:
            if data.activity_duration_seconds == 0:
                # update temp values
                data.activity_duration_seconds = user.activity_duration_seconds
                data.score = user.score

            data.users.append(
                DestinyActivityDetailsUsersModel(
                    bungie_name=user.bungie_name,
                    destiny_id=user.destiny_id,
                    system=user.system,
                    character_id=user.character_id,
                    character_class=user.character_class,
                    light_level=user.light_level,
                    completed=True if user.completed == 1 else False,
                    kills=user.kills,
                    deaths=user.deaths,
                    assists=user.assists,
                    time_played_seconds=user.time_played_seconds,
                )
            )

        return data

    async def update_activity_db(self, entry_time: Optional[datetime.datetime] = None):
        """Gets this user's not-saved history and saves it in the db"""

        async def handle(i: int, t: datetime.datetime) -> Optional[list[int, datetime.datetime, dict]]:
            """Get pgcr"""

            try:
                pgcr = await self.get_pgcr(i)

            except CustomException:
                logger.warning("Failed getting pgcr <%s>", i)

                # remove the instance_id from the cache
                cache.saved_pgcrs.remove(i)

                # looks like it failed, lets try again later
                await crud_activities_fail_to_get.insert(db=self.db, instance_id=i, period=t)

                return
            return [i, t, pgcr.content]

        async def input_data(gather_instance_ids: list[int], gather_activity_times: list[datetime.datetime]):
            """Gather all pgcr and insert them"""

            results = await asyncio.gather(*[handle(i, t) for i, t in zip(gather_instance_ids, gather_activity_times)])

            # do this with a separate DB session, do make smaller commits
            async with get_async_session().begin() as session:
                for result in results:
                    if result:
                        i = result[0]
                        t = result[1]
                        pgcr = result[2]

                        # insert information to DB
                        await crud_activities.insert(db=session, instance_id=i, activity_time=t, pgcr=pgcr)

        # get the logger
        logger = logging.getLogger("updateActivityDb")

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

            instance_id = int(activity["activityDetails"]["instanceId"])
            activity_time: datetime.datetime = activity["period"]

            # update with the newest entry timestamp
            if activity_time > entry_time:
                entry_time = activity_time

            # needs to be same from gathers
            async with asyncio.Lock():
                # check if info is already in DB, skip if so. query the cache first
                if instance_id in cache.saved_pgcrs:
                    continue

                # add the instance_id to the cache to prevent other users with the same instance to double check this
                # will get removed again if something fails
                cache.saved_pgcrs.add(instance_id)

                # check if the cache is maybe just wrong
                if await crud_activities.get(db=self.db, instance_id=instance_id) is not None:
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

        # update them with the newest entry timestamp
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

    async def get_solos(self) -> DestinyLowMansModel:
        """Return the destiny solos"""

        interesting_solos = await destiny_manifest.get_challenging_solo_activities(db=self.db)

        # get the results for this in a gather (keeps order)
        results = await asyncio.gather(
            *[
                self.get_lowman_count(activity_ids=activity.activity_ids, max_player_count=1)
                for activity in interesting_solos
            ]
        )
        solos = DestinyLowMansModel()

        # loop through the results
        for result, activity in zip(results, interesting_solos):
            solos.solos.append(DestinyUpdatedLowManModel(activity_name=activity.name, **result.dict()))

        return solos

    async def get_activity_stats(
        self,
        activity_ids: Optional[list[int]] = None,
        mode: Optional[int] = None,
        character_class: Optional[str] = None,
        character_ids: Optional[list[int]] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
    ) -> DestinyActivityOutputModel:
        """Return the user's stats for the activity"""

        allow_time_period = None
        if start_time or end_time:
            allow_time_period = [
                TimePeriodModel(start_time=start_time or datetime.datetime.min, end_time=end_time or get_now_with_tz())
            ]

        data = await crud_activities.get_activities(
            db=self.db,
            activity_hashes=activity_ids,
            mode=mode,
            destiny_id=self.destiny_id,
            allow_time_periods=allow_time_period,
            character_class=character_class,
            character_ids=character_ids,
        )

        # get output model
        result = DestinyActivityOutputModel(
            full_completions=0,
            cp_completions=0,
            kills=0,
            precision_kills=0,
            deaths=0,
            assists=0,
            time_spend=datetime.timedelta(seconds=0),
            fastest=None,
            fastest_instance_id=None,
            average=datetime.timedelta(seconds=0),
        )

        # save some stats for each activity. needed because a user can participate with multiple characters in an activity
        # key: instance_id
        activities_time_played: dict[int, datetime.timedelta] = {}
        activities_completed: dict[int, bool] = {}

        # loop through all results
        for activity_stats in data:
            result.kills += activity_stats.kills
            result.precision_kills += activity_stats.precision_kills
            result.deaths += activity_stats.deaths
            result.assists += activity_stats.assists
            result.time_spend += datetime.timedelta(seconds=activity_stats.time_played_seconds)

            # register the activity completion (with all chars)
            if (activity_stats.activity_instance_id not in activities_completed) or (
                not activities_completed[activity_stats.activity_instance_id] and activity_stats.completed
            ):
                activities_completed.update({activity_stats.activity_instance_id: activity_stats.completed})

            # register the activity duration (once, same for all chars)
            if activity_stats.activity_instance_id not in activities_time_played:
                activities_time_played.update(
                    {
                        activity_stats.activity_instance_id: datetime.timedelta(
                            seconds=activity_stats.activity_duration_seconds
                        )
                    }
                )

        # get the completion count
        result.full_completions = sum(activities_completed.values())
        result.cp_completions = len(activities_completed) - result.full_completions

        # get the fastest / average time
        activities_completed_time_played: dict[int, datetime.timedelta] = {}
        for completed_id, completed in activities_completed.items():
            if completed:
                activities_completed_time_played.update({completed_id: activities_time_played[completed_id]})
        result.fastest_instance_id = min(activities_completed_time_played, key=activities_completed_time_played.get)
        result.fastest = activities_completed_time_played[result.fastest_instance_id]
        result.average = sum(activities_completed_time_played.values(), datetime.timedelta(seconds=0)) / len(
            activities_completed_time_played
        )

        return result
