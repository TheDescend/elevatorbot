import dataclasses
from typing import Optional

from dis_snek.client import Snake
from dis_snek.models import Guild, Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.backendNetworking.routes import destiny_activities_get_all_route
from ElevatorBot.static.destinyEnums import ModeScope
from NetworkingSchemas.destiny.activities import (
    DestinyActivitiesModel,
    DestinyActivityDetailsModel,
)


@dataclasses.dataclass
class DestinyActivities(BaseBackendConnection):
    client: Optional[Snake]
    discord_guild: Optional[Guild]
    discord_member: Optional[Member]

    async def get_all(self) -> BackendResult:
        """Get all activities"""

        result = await self._backend_request(
            method="GET",
            route=destiny_activities_get_all_route,
        )

        if result:
            # convert to correct pydantic model
            result.result = DestinyActivitiesModel.parse_obj(result.result)
        return result

    async def last(
        self,
        activity_ids: Optional[list[int]] = None,  # if this is supplied, mode is ignored
        mode: Optional[ModeScope] = ModeScope.ALL,
        character_class: Optional[str] = None,
        completed: bool = True,
    ) -> BackendResult:
        """Get the last activity"""

        result = await self._backend_request(
            method="GET",
            route=destiny_activities_get_all_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
            data={
                "completed": completed,
                "activity_ids": activity_ids,
                "mode": mode,
                "character_class": character_class,
            },
        )

        if result:
            # convert to correct pydantic model
            result.result = DestinyActivityDetailsModel.parse_obj(result.result)
        return result
