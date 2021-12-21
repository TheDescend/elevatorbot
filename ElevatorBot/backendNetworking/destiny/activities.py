import dataclasses
from typing import Optional

from dis_snek.models import Guild, Member
from orjson import orjson

from DestinyEnums.enums import UsableDestinyActivityModeTypeEnum
from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.routes import (
    destiny_activities_activity_route,
    destiny_activities_get_all_route,
    destiny_activities_get_grandmaster_route,
    destiny_activities_last_route,
)

from NetworkingSchemas.destiny.activities import (
    DestinyActivitiesModel,
    DestinyActivityDetailsModel,
    DestinyActivityInputModel,
    DestinyActivityOutputModel,
)


@dataclasses.dataclass
class DestinyActivities(BaseBackendConnection):
    discord_guild: Optional[Guild]
    discord_member: Optional[Member]

    async def get_all(self) -> Optional[DestinyActivitiesModel]:
        """Get all activities"""

        result = await self._backend_request(
            method="GET",
            route=destiny_activities_get_all_route,
        )

        # convert to correct pydantic model
        return DestinyActivitiesModel.parse_obj(result.result) if result else None

    async def get_grandmaster(self) -> Optional[DestinyActivitiesModel]:
        """Get all grandmaster nfs"""

        result = await self._backend_request(
            method="GET",
            route=destiny_activities_get_grandmaster_route,
        )

        # convert to correct pydantic model
        return DestinyActivitiesModel.parse_obj(result.result) if result else None

    async def last(
        self,
        activity_ids: Optional[list[int]] = None,  # if this is supplied, mode is ignored
        mode: UsableDestinyActivityModeTypeEnum = UsableDestinyActivityModeTypeEnum.ALL,
        character_class: Optional[str] = None,
        completed: bool = True,
    ) -> Optional[DestinyActivityDetailsModel]:
        """Get the last activity"""

        # todo use pydantic model
        result = await self._backend_request(
            method="POST",
            route=destiny_activities_last_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
            data={
                "completed": completed,
                "activity_ids": activity_ids,
                "mode": mode,
                "character_class": character_class,
            },
        )

        # convert to correct pydantic model
        return DestinyActivityDetailsModel.parse_obj(result.result) if result else None

    async def get_activity_stats(self, input_model: DestinyActivityInputModel) -> Optional[DestinyActivityOutputModel]:
        """Get all activities"""

        result = await self._backend_request(
            method="POST",
            route=destiny_activities_activity_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
            data=input_model,
        )

        # convert to correct pydantic model
        return DestinyActivityOutputModel.parse_obj(result.result) if result else None
