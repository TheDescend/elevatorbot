import asyncio
import datetime
from typing import Optional

from bungio.models import DestinyPostGameCarnageReportData
from bungio.models.base import MISSING
from sqlalchemy import distinct, func, not_, select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud.base import CRUDBase
from Backend.database import acquire_db_session
from Backend.database.models import Activities, ActivitiesFailToGet, ActivitiesUsers, ActivitiesUsersWeapons
from Shared.networkingSchemas.destiny.roles import TimePeriodModel

fail_to_get_insert_lock = asyncio.Lock()
delete_lock = asyncio.Lock()
insert_lock = asyncio.Lock()


starting_phase_cutoff = datetime.datetime(day=22, month=2, year=2022, hour=17, tzinfo=datetime.timezone.utc)


class CRUDActivitiesFailToGet(CRUDBase):
    async def get_all(self, db: AsyncSession) -> list[ActivitiesFailToGet]:
        """Get all missing pgcr ids"""

        return await self._get_all(db=db)

    async def insert(self, db: AsyncSession, instance_id: int, period: datetime.datetime):
        """Insert missing pgcr"""

        async with fail_to_get_insert_lock:
            if await self._get_with_key(db=db, primary_key=instance_id) is None:
                await self._insert(db=db, to_create=ActivitiesFailToGet(instance_id=instance_id, period=period))

    async def delete(self, db: AsyncSession, obj: ActivitiesFailToGet):
        """Insert missing pgcr"""

        async with delete_lock:
            await self._delete(db=db, obj=obj)


class CRUDActivities(CRUDBase):
    async def get(self, db: AsyncSession, instance_id: int) -> Optional[Activities]:
        """Get the activity with the instance_id"""

        return await self._get_with_key(db=db, primary_key=instance_id)

    async def insert(self, data: list[tuple[int, datetime.datetime, DestinyPostGameCarnageReportData]]):
        """Get the activity with the instance_id"""

        to_create = []
        for instance_id, activity_time, pgcr in data:
            to_create.append(self._convert_to_model(instance_id=instance_id, activity_time=activity_time, pgcr=pgcr))

        async with acquire_db_session() as session:
            await self._insert_multi(db=session, to_create=to_create)

    @staticmethod
    def _convert_to_model(
        instance_id: int, activity_time: datetime.datetime, pgcr: DestinyPostGameCarnageReportData
    ) -> Activities:
        """Actually do the insert"""

        # starting phase index is only the way to go before 22/2/22, after we should use activityWasStartedFromBeginning
        if activity_time > starting_phase_cutoff:
            starting_phase_index = 0 if pgcr.activity_was_started_from_beginning else 99
        else:
            starting_phase_index = pgcr.starting_phase_index

        # build the activity
        activity = Activities(
            instance_id=instance_id,
            period=activity_time,
            reference_id=pgcr.activity_details.reference_id,
            director_activity_hash=pgcr.activity_details.director_activity_hash,
            starting_phase_index=starting_phase_index,
            mode=pgcr.activity_details.mode.value,
            modes=[mode.value for mode in pgcr.activity_details.modes],
            is_private=pgcr.activity_details.is_private,
            system=pgcr.activity_details.membership_type.value,
        )

        # loop through the members of the activity and append that data
        for player_pgcr in pgcr.entries:
            # get the bungie name separately, since bungie decided it would be fun to pass it as an empty string if it does not exist yet
            try:
                bungie_name = player_pgcr.player.destiny_user_info.bungie_global_display_name
                if bungie_name == "" or bungie_name is MISSING:
                    bungie_name = player_pgcr.player.destiny_user_info.display_name
                    bungie_code = "0000"
                else:
                    bungie_code = str(player_pgcr.player.destiny_user_info.bungie_global_display_name_code).zfill(4)
            except AttributeError:
                # sometimes do not even pass the field, very fun
                bungie_name = "UnknownName"
                bungie_code = "0000"

            extended_data = player_pgcr.extended or None
            player = ActivitiesUsers(
                destiny_id=player_pgcr.player.destiny_user_info.membership_id,
                bungie_name=f"{bungie_name}#{bungie_code}",
                character_id=player_pgcr.character_id,
                character_class=player_pgcr.player.character_class or None,
                character_level=player_pgcr.player.character_level,
                system=player_pgcr.player.destiny_user_info.membership_type.value,
                light_level=player_pgcr.player.light_level,
                emblem_hash=player_pgcr.player.emblem_hash,
                standing=player_pgcr.standing,
                assists=int(player_pgcr.values["assists"].basic.value),
                completed=int(player_pgcr.values["completed"].basic.value),
                deaths=int(player_pgcr.values["deaths"].basic.value),
                kills=int(player_pgcr.values["kills"].basic.value),
                opponents_defeated=int(player_pgcr.values["opponentsDefeated"].basic.value),
                efficiency=player_pgcr.values["efficiency"].basic.value,
                kills_deaths_ratio=player_pgcr.values["killsDeathsRatio"].basic.value,
                kills_deaths_assists=player_pgcr.values["killsDeathsAssists"].basic.value,
                score=int(player_pgcr.values["score"].basic.value),
                activity_duration_seconds=int(player_pgcr.values["activityDurationSeconds"].basic.value),
                completion_reason=int(player_pgcr.values["completionReason"].basic.value),
                start_seconds=int(player_pgcr.values["startSeconds"].basic.value),
                time_played_seconds=int(player_pgcr.values["timePlayedSeconds"].basic.value),
                player_count=int(player_pgcr.values["playerCount"].basic.value),
                team_score=int(player_pgcr.values["teamScore"].basic.value),
                precision_kills=int(extended_data.values["precisionKills"].basic.value) if extended_data else 0,
                weapon_kills_grenade=int(extended_data.values["weaponKillsGrenade"].basic.value)
                if extended_data
                else 0,
                weapon_kills_melee=int(extended_data.values["weaponKillsMelee"].basic.value) if extended_data else 0,
                weapon_kills_super=int(extended_data.values["weaponKillsSuper"].basic.value) if extended_data else 0,
                weapon_kills_ability=int(extended_data.values["weaponKillsAbility"].basic.value)
                if extended_data
                else 0,
            )

            if extended_data:
                # loop through the weapons the player used and append that data
                if extended_data.weapons:
                    for weapon_pgcr in extended_data.weapons:
                        weapon = ActivitiesUsersWeapons(
                            weapon_id=weapon_pgcr.reference_id,
                            unique_weapon_kills=int(weapon_pgcr.values["uniqueWeaponKills"].basic.value),
                            unique_weapon_precision_kills=int(
                                weapon_pgcr.values["uniqueWeaponPrecisionKills"].basic.value
                            ),
                        )

                        # append weapon data to player
                        player.weapons.append(weapon)

            # append player data to activity
            activity.users.append(player)

        return activity

    async def get_activities(
        self,
        db: AsyncSession,
        destiny_id: int,
        activity_hashes: Optional[list[int]] = None,
        mode: Optional[int] = None,
        only_completed: bool = True,
        no_checkpoints: bool = True,
        only_checkpoint: bool = False,
        require_team_flawless: bool = False,
        require_individual_flawless: bool = False,
        character_class: Optional[str] = None,
        character_ids: Optional[list[int]] = None,
        maximum_allowed_players: Optional[int] = None,
        require_score: Optional[int] = None,
        require_kills: Optional[int] = None,
        require_kills_per_minute: Optional[float] = None,
        require_kda: Optional[float] = None,
        require_kd: Optional[float] = None,
        allow_time_periods: Optional[list[TimePeriodModel]] = None,
        disallow_time_periods: Optional[list[TimePeriodModel]] = None,
    ) -> list[ActivitiesUsers]:
        """Gets a list of all Activities that fulfill the get_requirements"""

        query = select(ActivitiesUsers)
        query = query.join(Activities)
        query = query.group_by(ActivitiesUsers.id)

        query = query.filter(ActivitiesUsers.destiny_id == destiny_id)

        # filter activity hashes
        if activity_hashes:
            query = query.filter(Activities.director_activity_hash.in_(activity_hashes))

        # filter mode
        if mode:
            query = query.filter(Activities.modes.any(mode))

        # do we accept non checkpoint runs?
        if no_checkpoints:
            query = query.filter(Activities.starting_phase_index == 0)
        if only_checkpoint:
            query = query.filter(Activities.starting_phase_index != 0)

        # team flawless required?
        if require_team_flawless:
            subquery = select(Activities.instance_id)
            subquery = subquery.join(ActivitiesUsers)
            subquery = subquery.group_by(Activities.instance_id)

            subquery = subquery.having(func.sum(distinct(ActivitiesUsers.deaths)) == 0)

            query = query.filter(Activities.instance_id.in_(subquery))

        # check completion status
        if only_completed:
            query = query.filter(ActivitiesUsers.completed == 1)
        query = query.filter(ActivitiesUsers.completion_reason == 0)

        # individual flawless required?
        if require_individual_flawless:
            query = query.filter(ActivitiesUsers.deaths == 0)

        # limit character class
        if character_class:
            query = query.filter(ActivitiesUsers.character_class == character_class)

        # limit character ids
        if character_ids:
            query = query.filter(ActivitiesUsers.character_id.in_(character_ids))

        # minimum score?
        if require_score:
            query = query.filter(ActivitiesUsers.score > require_score)

        # minimum kills?
        if require_kills:
            query = query.filter(ActivitiesUsers.kills >= require_kills)

        # minimum kills per minute?
        if require_kills_per_minute:
            query = query.filter(
                (ActivitiesUsers.kills * 60 / ActivitiesUsers.time_played_seconds) >= require_kills_per_minute
            )

        # minimum kda?
        if require_kda:
            query = query.filter(ActivitiesUsers.kills_deaths_assists >= require_kda)

        # minimum kd?
        if require_kd:
            query = query.filter(ActivitiesUsers.kills_deaths_ratio >= require_kd)

        # do we have allowed datetimes
        if allow_time_periods:
            for time in allow_time_periods:
                query = query.filter(Activities.period.between(time.start_time, time.end_time))

        # do we have disallowed datetimes
        if disallow_time_periods:
            for time in disallow_time_periods:
                query = query.filter(not_(Activities.period.between(time.start_time, time.end_time)))

        # limit max users to player_count
        if maximum_allowed_players is not None:
            subquery = select(Activities.instance_id)
            subquery = subquery.join(ActivitiesUsers)
            subquery = subquery.group_by(Activities.instance_id)

            subquery = subquery.having(func.count(distinct(ActivitiesUsers.destiny_id)) <= maximum_allowed_players)

            query = query.filter(Activities.instance_id.in_(subquery))

        result = await self._execute_query(db=db, query=query)
        scalars = result.scalars().fetchall()
        return scalars

    async def get_last_activity(
        self,
        db: AsyncSession,
        destiny_id: int,
        mode: Optional[int] = None,
        activity_ids: Optional[list[int]] = None,
        completed: bool = True,
        character_class: Optional[str] = None,
    ) -> Activities:
        """Gets a list of all Activities that fulfill the get_requirements"""

        query = select(Activities)
        query = query.join(ActivitiesUsers)

        # check mode
        if mode and not activity_ids:
            query = query.filter(Activities.modes.any(mode))

        # check activity_ids
        if activity_ids:
            query = query.filter(Activities.director_activity_hash.in_(activity_ids))

        # filter the destiny id
        query = query.filter(ActivitiesUsers.destiny_id == destiny_id)

        # limit the class
        if character_class:
            query = query.filter(ActivitiesUsers.character_class == character_class)

        # check completion status
        if completed:
            query = query.filter(ActivitiesUsers.completed == 1)

        # oder them by the latest first
        query = query.order_by(Activities.period.desc())

        result = await self._execute_query(db=db, query=query)
        result = result.scalar()

        if not result:
            raise CustomException("NoActivityFound")

        return result

    async def calculate_time_played(
        self,
        db: AsyncSession,
        destiny_id: int,
        mode: int = 0,
        activity_ids: Optional[list[int]] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        character_class: Optional[str] = None,
    ) -> int:
        """Calculate the time played (in seconds) from the DB"""

        query = select(func.sum(ActivitiesUsers.time_played_seconds))
        query = query.join(Activities)

        # filter mode
        if mode != 0:
            query = query.filter(Activities.modes.any(mode))

        # filter activities
        if activity_ids:
            query = query.filter(Activities.reference_id.in_(activity_ids))

        # limit to the allowed times if that is requested
        if start_time:
            query = query.filter(Activities.period >= start_time)
        if end_time:
            query = query.filter(Activities.period <= end_time)

        # filter the destiny id
        query = query.filter(ActivitiesUsers.destiny_id == destiny_id)

        # limit the class
        if character_class:
            query = query.filter(ActivitiesUsers.character_class == character_class)

        result = await self._execute_query(db=db, query=query)
        result = result.scalar()

        # I heard this can return None instead of 0, so we're doing this
        return result if result else 0


crud_activities_fail_to_get = CRUDActivitiesFailToGet(ActivitiesFailToGet)
crud_activities = CRUDActivities(Activities)
