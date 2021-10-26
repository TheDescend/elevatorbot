import dataclasses

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.backendNetworking.routes import activities_get_all_route


@dataclasses.dataclass
class DestinyActivities(BaseBackendConnection):
    async def get_all(self) -> BackendResult:
        """Get all activities"""

        return await self._backend_request(
            method="GET",
            route=activities_get_all_route,
        )
