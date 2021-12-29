import dataclasses

from dis_snek.models import Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.routes import steam_player_get_route
from NetworkingSchemas.destiny.steamPlayers import DestinySteamPlayersCountModel


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
