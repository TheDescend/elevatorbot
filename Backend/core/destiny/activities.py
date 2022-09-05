import asyncio
import dataclasses
import datetime
import logging
from typing import Optional

from anyio import create_task_group, to_thread
from bungio.error import BungieDead, BungIOException
from bungio.models import DestinyActivityModeType, DestinyPostGameCarnageReportData
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.bungio.client import get_bungio_client
from Backend.bungio.manifest import destiny_manifest
from Backend.core.destiny.clan import DestinyClan
from Backend.core.errors import CustomException
from Backend.crud import crud_activities, crud_activities_fail_to_get, discord_users
from Backend.database.base import acquire_db_session
from Backend.database.models import ActivitiesUsers, DiscordUsers
from Backend.misc.cache import cache
from Shared.functions.helperFunctions import get_now_with_tz
from Shared.networkingSchemas.destiny import (
    DestinyActivityDetailsModel,
    DestinyActivityDetailsUsersModel,
    DestinyActivityModel,
    DestinyActivityOutputModel,
    DestinyLowManModel,
    DestinyLowMansByCategoryModel,
    DestinyLowMansModel,
    DestinyUpdatedLowManModel,
)
from Shared.networkingSchemas.destiny.roles import TimePeriodModel

update_missing_pgcr_lock = asyncio.Lock()
input_data_lock = asyncio.Lock()

pgcr_getter_semaphore = asyncio.Semaphore(100)


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

    async def get_lowman_count(
        self,
        activity_ids: list[int],
        max_player_count: int,
        require_flawless: bool = False,
        no_checkpoints: bool = True,
        disallowed_datetimes: Optional[list[TimePeriodModel]] = None,
        score_threshold: Optional[int] = None,
        min_kills_per_minute: Optional[float] = None,
        db: Optional[AsyncSession] = None,
    ) -> DestinyLowManModel:
        """Returns low man data. If results gets passed, the result gets added to that list too"""

        # get player data
        low_activity_info = await crud_activities.get_activities(
            db=db or self.db,
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
        count, flawless_count, not_flawless_count, fastest, fastest_instance_id = await to_thread.run_sync(
            get_lowman_count_subprocess, low_activity_info
        )
        result = DestinyLowManModel(
            activity_ids=activity_ids,
            count=count,
            flawless_count=flawless_count,
            not_flawless_count=not_flawless_count,
            fastest=fastest,
            fastest_instance_id=fastest_instance_id,
        )

        return result

    async def update_missing_pgcr(self):
        """Insert the missing pgcr"""

        async with update_missing_pgcr_lock:
            if not (missing := await crud_activities_fail_to_get.get_all(db=self.db)):
                return

            # get the destiny clan members for descend
            async with acquire_db_session() as session:
                clan = DestinyClan(db=session, guild_id=-1)
                descend_clan_members = await clan.get_descend_clan_members()

            for activity in missing:
                # check if info is already in DB, delete and skip if so
                result = await crud_activities.get(db=self.db, instance_id=activity.instance_id)
                if result:
                    await crud_activities_fail_to_get.delete(db=self.db, obj=activity)
                    continue

                # get PGCR
                try:
                    pgcr = await get_bungio_client().api.get_post_game_carnage_report(activity_id=activity.instance_id)
                except BungIOException:
                    # only continue if we get a response this time
                    continue

                # add info to DB
                await crud_activities.insert(
                    data=[(activity.instance_id, activity.period, pgcr)], descend_clan_members=descend_clan_members
                )

                # delete from to-do DB
                await crud_activities_fail_to_get.delete(db=self.db, obj=activity)
                cache.saved_pgcrs.add(activity.instance_id)

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
            # get the registered user data
            try:
                profile = await discord_users.get_profile_from_destiny_id(db=self.db, destiny_id=user.destiny_id)
                profile = profile.discord_id
            except CustomException:
                profile = None

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
                    discord_id=profile,
                )
            )

        return data

    async def update_activity_db(self, entry_time: Optional[datetime.datetime] = None):
        """Gets this user's not-saved history and saves it in the db"""

        async def handle(
            results: list[tuple[int, datetime.datetime, DestinyPostGameCarnageReportData]], i: int, t: datetime.datetime
        ):
            """Get pgcr"""

            try:
                async with pgcr_getter_semaphore:
                    pgcr = await get_bungio_client().api.get_post_game_carnage_report(i)
                    results.append((i, t, pgcr))

            except Exception as e:
                # stop everything if bungie is ded
                if isinstance(e, BungieDead):
                    raise e

                # log that
                logger_exceptions.exception(f"Failed getting PGCR `{i}`", exc_info=e)

                # remove the instance_id from the cache
                cache.saved_pgcrs.remove(i)

                # looks like it failed, lets try again later
                async with acquire_db_session() as db:
                    await crud_activities_fail_to_get.insert(db=db, instance_id=i, period=t)

        async def input_data(gather_instances: dict[int, datetime.datetime]):
            """Gather all pgcr and insert them"""

            # get the data with anyio tasks
            results: list[tuple[int, datetime.datetime, DestinyPostGameCarnageReportData]] = []
            async with create_task_group() as tg:
                for i, t in gather_instances.items():
                    tg.start_soon(lambda: handle(results=results, i=i, t=t))

            # insert information to DB
            await crud_activities.insert(data=results, descend_clan_members=descend_clan_members)

        # get the logger
        logger = logging.getLogger("updateActivityDb")
        logger_exceptions = logging.getLogger("updateActivityDbExceptions")

        # get the destiny clan members for descend
        async with acquire_db_session() as session:
            clan = DestinyClan(db=session, guild_id=-1)
            descend_clan_members = await clan.get_descend_clan_members()

        try:
            async with input_data_lock:
                # ignore this if the same user is currently running
                if self.destiny_id in cache.updater_running_updates:
                    logger.info(f"Skipping duplicate activity DB update for destinyID `{self.destiny_id}`")
                    return
                else:
                    cache.updater_running_updates.add(self.destiny_id)

            # save the start time, so we can update the user afterwards
            start_time = None

            # get the entry time
            if not entry_time:
                entry_time = self.user.activities_last_updated

            logger.info(f"Starting activity DB update for destinyID `{self.destiny_id}`")

            # loop through all activities
            try:
                async for activity in self.user.bungio_user.yield_activity_history(
                    mode=DestinyActivityModeType.NONE, earliest_allowed_datetime=entry_time, auth=self.user.auth
                ):
                    instance_id = activity.activity_details.instance_id

                    # save the youngest start time
                    if (not start_time) or (activity.period > start_time):
                        start_time = activity.period

                    # needs to be same for anyio tasks
                    async with input_data_lock:
                        # check if info is already in DB, skip if so. query the cache first
                        if instance_id in cache.saved_pgcrs:
                            continue

                        # add the instance_id to the cache to prevent other users with the same instance to double-check this
                        # will get removed again if something fails
                        cache.saved_pgcrs.add(instance_id)

                        # check if the cache is maybe just wrong
                        if await crud_activities.get(db=self.db, instance_id=instance_id) is not None:
                            continue

                        # add to task list
                        cache.updater_instances.update({instance_id: activity.period})

                # insert the missing activities
                async with input_data_lock:
                    if cache.updater_instances:
                        to_get_instances = cache.updater_instances
                        cache.updater_instances = {}
                    else:
                        to_get_instances = {}

                # get and input the data
                await input_data(to_get_instances)

            except BungIOException as e:
                # catch when bungie is down and ignore it
                if isinstance(e, BungieDead):
                    return
                raise e

            # update them with the newest entry timestamp
            if start_time:
                await discord_users.update(db=self.db, to_update=self.user, activities_last_updated=start_time)

            logger.info(f"Done with activity DB update for destinyID `{self.destiny_id}`")

        except Exception as error:
            # log that
            logger_exceptions.exception(f"Activity DB update for destinyID `{self.destiny_id}`", exc_info=error)

        cache.updater_running_updates.remove(self.destiny_id)

    async def get_solos(self) -> DestinyLowMansByCategoryModel:
        """Return the destiny solos"""

        async def get_by_topic(t_category: str, t_activities: list[DestinyActivityModel]):
            """Get the activities by topic"""

            # get the activities in anyio tasks
            # allow cp runs for raids
            results: list[DestinyLowManModel] = []
            async with acquire_db_session() as db:
                for activity in t_activities:
                    results.append(
                        await self.get_lowman_count(
                            db=db,
                            activity_ids=activity.activity_ids,
                            max_player_count=1,
                            require_flawless=False,
                            no_checkpoints=activity.mode != DestinyActivityModeType.RAID.value,
                        )
                    )

            # loop through the results
            # first loop through the activities since we want them ordered
            # a bit inefficient but fine really
            solos: list[DestinyUpdatedLowManModel] = []
            for t_activity in t_activities:
                for result in results:
                    if t_activity.activity_ids == result.activity_ids:
                        solos.append(DestinyUpdatedLowManModel(activity_name=t_activity.name, **result.dict()))
                        break

            # get the correct category and append there
            for entry in solos_by_categories.categories:
                if entry.category == t_category:
                    entry.solos = solos

        interesting_solos = await destiny_manifest.get_challenging_solo_activities()

        # get the results for all categories in anyio tasks
        solos_by_categories = DestinyLowMansByCategoryModel()
        async with create_task_group() as tg:
            for category, activities in interesting_solos.items():
                solos_by_categories.categories.append(DestinyLowMansModel(category=category))
                tg.start_soon(get_by_topic, category, activities)

        return solos_by_categories

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

        data_full = await crud_activities.get_activities(
            db=self.db,
            activity_hashes=activity_ids,
            mode=mode,
            destiny_id=self.destiny_id,
            allow_time_periods=allow_time_period,
            character_class=character_class,
            character_ids=character_ids,
            no_checkpoints=True,
            only_completed=False,
        )
        data_cp = await crud_activities.get_activities(
            db=self.db,
            activity_hashes=activity_ids,
            mode=mode,
            destiny_id=self.destiny_id,
            allow_time_periods=allow_time_period,
            character_class=character_class,
            character_ids=character_ids,
            no_checkpoints=False,
            only_checkpoint=True,
            only_completed=False,
        )

        # get output model
        result = await to_thread.run_sync(get_activity_stats_subprocess, data_full, data_cp)

        return result


async def update_activities_in_background(user: DiscordUsers):
    """Gets called when a user first registers and updates their activities in the background"""
    async with acquire_db_session() as db:
        activities = DestinyActivities(db=db, user=user)
        await activities.update_activity_db()


def get_lowman_count_subprocess(
    low_activity_info: list[ActivitiesUsers],
) -> tuple[int, int, int, Optional[datetime.timedelta], Optional[int]]:
    """Run in anyio subprocess on another thread since this might be slow"""

    count, flawless_count, not_flawless_count, fastest, fastest_instance_id = 0, 0, 0, None, None

    for solo in low_activity_info:
        count += 1
        if solo.deaths == 0:
            flawless_count += 1
        else:
            not_flawless_count += 1
        if not fastest or (solo.time_played_seconds < fastest.seconds):
            fastest = datetime.timedelta(seconds=solo.time_played_seconds)
            fastest_instance_id = solo.activity_instance_id

    return count, flawless_count, not_flawless_count, fastest, fastest_instance_id


def get_activity_stats_subprocess(
    data_full: list[ActivitiesUsers], data_cp: list[ActivitiesUsers]
) -> DestinyActivityOutputModel:
    """Run in anyio subprocess on another thread since this might be slow"""

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
        average=None,
    )

    # save some stats for each activity. needed because a user can participate with multiple characters in an activity
    # key: instance_id
    activities_time_played: dict[int, datetime.timedelta] = {}
    activities_total: list[int] = []
    activities_completed: list[int] = []

    # loop through all results
    for activity_stats in data_cp + data_full:
        result.kills += activity_stats.kills
        result.precision_kills += activity_stats.precision_kills
        result.deaths += activity_stats.deaths
        result.assists += activity_stats.assists
        result.time_spend += datetime.timedelta(seconds=activity_stats.time_played_seconds)

        # register all activity completions
        if activity_stats.activity_instance_id not in activities_total:
            if bool(activity_stats.completed):
                activities_total.append(activity_stats.activity_instance_id)

    for activity_stats in data_full:
        # register the full activity completions (with all chars)
        if activity_stats.activity_instance_id not in activities_completed:
            if bool(activity_stats.completed):
                activities_completed.append(activity_stats.activity_instance_id)

        # register the activity duration (once, same for all chars)
        if activity_stats.activity_instance_id not in activities_time_played:
            activities_time_played[activity_stats.activity_instance_id] = datetime.timedelta(seconds=0)
        activities_time_played[activity_stats.activity_instance_id] += datetime.timedelta(
            seconds=activity_stats.activity_duration_seconds
        )

    result.full_completions = len(activities_completed)
    result.cp_completions = len(activities_total) - result.full_completions

    # make sure the fastest / average activity was completed
    activities_time_played = {
        activity_id: time_played
        for activity_id, time_played in activities_time_played.items()
        if activity_id in activities_completed
    }

    # only do that if they actually played an activity tho
    if activities_time_played:
        result.fastest_instance_id = min(activities_time_played, key=activities_time_played.get)
        result.fastest = activities_time_played[result.fastest_instance_id]
        result.average = sum(activities_time_played.values(), datetime.timedelta(seconds=0)) / len(
            activities_time_played
        )

    return result
