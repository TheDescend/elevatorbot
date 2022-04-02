import dataclasses

from dis_snek import Member

from ElevatorBot.networking.http import BaseBackendConnection
from ElevatorBot.networking.routes import steam_player_get_route
from Shared.networkingSchemas.destiny import DestinySteamPlayersCountModel


@dataclasses.dataclass
class SteamPlayers(BaseBackendConnection):
    discord_member: Member = dataclasses.field(init=False, default=None)

    async def get(self) -> DestinySteamPlayersCountModel:
        """Return the steam player count"""

        result = await self._backend_request(
            method="GET",
            route=steam_player_get_route,
        )

        # convert to correct pydantic model
        return DestinySteamPlayersCountModel.parse_obj(result.result)
