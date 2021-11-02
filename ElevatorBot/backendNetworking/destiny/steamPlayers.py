import dataclasses

from dis_snek.models import Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.backendNetworking.routes import steam_player_get_route


@dataclasses.dataclass
class SteamPlayers(BaseBackendConnection):
    discord_member: Member = dataclasses.field(init=False, default=None)

    async def get(self) -> BackendResult:
        """Return the steam player count"""

        return await self._backend_request(
            method="GET",
            route=steam_player_get_route,
        )
