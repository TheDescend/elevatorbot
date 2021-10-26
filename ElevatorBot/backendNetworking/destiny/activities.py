import dataclasses
from typing import Optional

from dis_snek.client import Snake
from dis_snek.models import Guild, Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.backendNetworking.routes import activities_get_all_route
from ElevatorBot.static.destinyEnums import ModeScope


@dataclasses.dataclass
class DestinyActivities(BaseBackendConnection):
    client: Optional[Snake]
    discord_guild: Optional[Guild]
    discord_member: Optional[Member]

    async def get_all(self) -> BackendResult:
        """Get all activities"""

        return await self._backend_request(
            method="GET",
            route=activities_get_all_route,
        )

    async def last(
        self,
        activity_ids: Optional[int] = None,  # if this is supplied, mode is ignored
        mode: Optional[ModeScope] = ModeScope.ALL,
        character_class: Optional[str] = None,
        completed: bool = True,
    ) -> BackendResult:
        """Get the last activity"""

        return await self._backend_request(
            method="GET",
            route=activities_get_all_route.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id),
            data={
                "completed": completed,
                "activity_ids": activity_ids,
                "mode": mode,
                "character_class": character_class,
            },
        )
