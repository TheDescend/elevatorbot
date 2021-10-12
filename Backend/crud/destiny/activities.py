import asyncio
import datetime

from sqlalchemy import distinct
from sqlalchemy import func
from sqlalchemy import not_
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.database.models import Activities
from Backend.database.models import ActivitiesFailToGet
from Backend.database.models import ActivitiesUsers
from Backend.database.models import ActivitiesUsersWeapons


class CRUDActivitiesFailToGet(CRUDBase):
    async def get_all(self, db: AsyncSession) -> list[ActivitiesFailToGet]:
        """Get all missing pgcr ids"""

        return await self._get_all(db=db)

    async def insert(self, db: AsyncSession, instance_id: int, period: datetime.datetime):
        """Insert missing pgcr"""

        if await self._get_with_key(db=db, primary_key=instance_id) is None:
            await self._insert(db=db, to_create=ActivitiesFailToGet(instance_id=instance_id, period=period))

    async def delete(self, db: AsyncSession, obj: ActivitiesFailToGet):
        """Insert missing pgcr"""

        await self._delete(db=db, obj=obj)


class CRUDActivities(CRUDBase):
    async def get(self, db: AsyncSession, instance_id: int) -> Activities | None:
        """Get the activity with the instance_id"""

        return await self._get_with_key(db=db, primary_key=instance_id)

    async def insert(self, db: AsyncSession, instance_id: int, activity_time: datetime, pgcr: dict):
        """Get the activity with the instance_id"""

        # get this to not accidentally insert the same thing twice
        async with asyncio.Lock():
            return await self.__locked_insert(db=db, instance_id=instance_id, activity_time=activity_time, pgcr=pgcr)

    async def __locked_insert(self, db: AsyncSession, instance_id: int, activity_time: datetime, pgcr: dict):
        """Actually do the insert"""

        # does the activity exist?
        if self.get(db=db, instance_id=instance_id):
            return

        to_create = []

        # build the activity
        activity = Activities(
            instance_id=instance_id,
            period=activity_time,
            reference_id=pgcr["activityDetails"]["referenceId"],
            director_activity_hash=pgcr["activityDetails"]["directorActivityHash"],
            starting_phase_index=pgcr["startingPhaseIndex"],
            mode=pgcr["activityDetails"]["mode"],
            modes=pgcr["activityDetails"]["modes"],
            is_private=pgcr["activityDetails"]["isPrivate"],
            system=pgcr["activityDetails"]["membershipType"],
        )

        # loop through the members of the activity and append that data
        for player_pgcr in pgcr["entries"]:
            player = ActivitiesUsers(
                destiny_id=player_pgcr["player"]["destinyUserInfo"]["membershipId"],
                character_id=player_pgcr["characterId"],
                character_class=player_pgcr["player"]["characterClass"]
                if "characterClass" in player_pgcr["player"]
                else None,
                character_level=player_pgcr["player"]["characterLevel"],
                system=player_pgcr["player"]["destinyUserInfo"]["membershipType"],
                light_level=player_pgcr["player"]["lightLevel"],
                emblem_hash=player_pgcr["player"]["emblemHash"],
                standing=player_pgcr["standing"],
                assists=int(player_pgcr["values"]["assists"]["basic"]["value"]),
                completed=int(player_pgcr["values"]["completed"]["basic"]["value"]),
                deaths=int(player_pgcr["values"]["deaths"]["basic"]["value"]),
                kills=int(player_pgcr["values"]["kills"]["basic"]["value"]),
                opponents_defeated=int(player_pgcr["values"]["opponentsDefeated"]["basic"]["value"]),
                efficiency=player_pgcr["values"]["efficiency"]["basic"]["value"],
                kills_deaths_ratio=player_pgcr["values"]["killsDeathsRatio"]["basic"]["value"],
                kills_deaths_assists=player_pgcr["values"]["killsDeathsAssists"]["basic"]["value"],
                score=int(player_pgcr["values"]["score"]["basic"]["value"]),
                activity_duration_seconds=int(player_pgcr["values"]["activityDurationSeconds"]["basic"]["value"]),
                completion_reason=int(player_pgcr["values"]["completionReason"]["basic"]["value"]),
                start_seconds=int(player_pgcr["values"]["startSeconds"]["basic"]["value"]),
                time_played_seconds=int(player_pgcr["values"]["timePlayedSeconds"]["basic"]["value"]),
                player_count=int(player_pgcr["values"]["playerCount"]["basic"]["value"]),
                team_score=int(player_pgcr["values"]["teamScore"]["basic"]["value"]),
                precision_kills=int(player_pgcr["extended"]["values"]["precisionKills"]["basic"]["value"]),
                weapon_kills_grenade=int(player_pgcr["extended"]["values"]["weaponKillsGrenade"]["basic"]["value"]),
                weapon_kills_melee=int(player_pgcr["extended"]["values"]["weaponKillsMelee"]["basic"]["value"]),
                weapon_kills_super=int(player_pgcr["extended"]["values"]["weaponKillsSuper"]["basic"]["value"]),
                weapon_kills_ability=int(player_pgcr["extended"]["values"]["weaponKillsAbility"]["basic"]["value"]),
            )

            # loop through the weapons the player used and append that data
            if "weapons" in player_pgcr["extended"]:
                for weapon_pgcr in player_pgcr["extended"]["weapons"]:
                    weapon = ActivitiesUsersWeapons(
                        weapon_id=weapon_pgcr["referenceId"],
                        unique_weapon_kills=int(weapon_pgcr["values"]["uniqueWeaponKills"]["basic"]["value"]),
                        unique_weapon_precision_kills=int(
                            weapon_pgcr["values"]["uniqueWeaponPrecisionKills"]["basic"]["value"]
                        ),
                    )

                    # append weapon data to player
                    to_create.append(weapon)
                    player.weapons.append(weapon)

            # append player data to activity
            to_create.append(player)
            activity.users.append(player)

        # append activity so it also gets inserted
        to_create.append(activity)

        # mass insert all the stuff to the db
        await self._insert_multi(db=db, to_create=to_create)

    async def get_activities(
        self,
        db: AsyncSession,
        activity_hashes: list[int],
        maximum_allowed_players: int,
        destiny_id: int,
        no_checkpoints: bool = True,
        require_team_flawless: bool = False,
        require_individual_flawless: bool = False,
        require_score: int = None,
        require_kills: int = None,
        require_kills_per_minute: float = None,
        require_kda: float = None,
        require_kd: float = None,
        allow_time_periods: list[dict] = None,  # see TimePeriodModel
        disallow_time_periods: list[dict] = None,  # see TimePeriodModel
    ) -> list[Activities]:
        """Gets a list of all Activities that fulfill the requirements"""

        query = select(Activities).filter(Activities.director_activity_hash.in_(activity_hashes))

        # do we accept non checkpoint runs?
        if no_checkpoints:
            query = query.filter(Activities.starting_phase_index == 0)

        # limit max users to player_count
        query = query.join(Activities.users)
        query = query.group_by(ActivitiesUsers.id)
        query = query.having(func.count(distinct(ActivitiesUsers.destiny_id)) <= maximum_allowed_players)

        # team flawless required?
        if require_team_flawless:
            query = query.having(func.count(distinct(ActivitiesUsers.deaths)) == 0)

        # check completion status
        query = query.filter(ActivitiesUsers.destiny_id == destiny_id)
        query = query.filter(ActivitiesUsers.completed == 1)
        query = query.filter(ActivitiesUsers.completion_reason == 0)

        # individual flawless required?
        if require_individual_flawless:
            query = query.filter(ActivitiesUsers.deaths == 0)

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
                start = time["start_time"]
                end = time["end_time"]
                query = query.filter(Activities.period.between(start, end))

        # do we have disallowed datetimes
        if disallow_time_periods:
            for time in disallow_time_periods:
                start = time["start_time"]
                end = time["end_time"]
                query = query.filter(not_(Activities.period.between(start, end)))

        result = await self._execute_query(db=db, query=query)
        return result.scalars().fetchall()


class CRUDActivitiesUsersStats(CRUDBase):
    pass


class CRUDActivitiesUsersStatsWeapons(CRUDBase):
    pass


activities_fail_to_get = CRUDActivitiesFailToGet(ActivitiesFailToGet)
activities = CRUDActivities(Activities)
activities_users_stats = CRUDActivitiesUsersStats(ActivitiesUsers)
activities_users_stats_weapons = CRUDActivitiesUsersStatsWeapons(ActivitiesUsersWeapons)
