import dataclasses
from typing import Optional

from dis_snek import Guild, Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.routes import (
    destiny_activities_activity_route,
    destiny_activities_get_all_route,
    destiny_activities_get_grandmaster_route,
    destiny_activities_last_route,
)
from Shared.enums.destiny import UsableDestinyActivityModeTypeEnum
from Shared.networkingSchemas.destiny import (
    DestinyActivitiesModel,
    DestinyActivityDetailsModel,
    DestinyActivityInputModel,
    DestinyActivityOutputModel,
    DestinyLastInputModel,
)


@dataclasses.dataclass
class DestinyActivities(BaseBackendConnection):
    discord_guild: Optional[Guild]
    discord_member: Optional[Member]

    async def get_all(self) -> DestinyActivitiesModel:
        """Get all activities"""

        result = await self._backend_request(
            method="GET",
            route=destiny_activities_get_all_route,
        )

        # convert to correct pydantic model
        return DestinyActivitiesModel.parse_obj(result.result)

    async def get_grandmaster(self) -> DestinyActivitiesModel:
        """Get all grandmaster nfs"""

        result = await self._backend_request(
            method="GET",
            route=destiny_activities_get_grandmaster_route,
        )

        # convert to correct pydantic model
        return DestinyActivitiesModel.parse_obj(result.result)

    async def last(
        self,
        activity_ids: Optional[list[int]] = None,  # if this is supplied, mode is ignored
        mode: UsableDestinyActivityModeTypeEnum = UsableDestinyActivityModeTypeEnum.ALL,
        character_class: Optional[str] = None,
        completed: bool = True,
    ) -> DestinyActivityDetailsModel:
        """Get the last activity"""

        result = await self._backend_request(
            method="POST",
            route=destiny_activities_last_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
            data=DestinyLastInputModel(
                completed=completed, activity_ids=activity_ids, mode=mode.value, character_class=character_class
            ),
        )

        # convert to correct pydantic model
        return DestinyActivityDetailsModel.parse_obj(result.result)

    async def get_activity_stats(self, input_model: DestinyActivityInputModel) -> DestinyActivityOutputModel:
        """Get all activities"""

        result = await self._backend_request(
            method="POST",
            route=destiny_activities_activity_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
            data=input_model,
        )

        # convert to correct pydantic model
        return DestinyActivityOutputModel.parse_obj(result.result)
