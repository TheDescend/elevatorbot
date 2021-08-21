import dataclasses
from typing import Optional

from ElevatorBot.core.http import BaseBackendConnection



@dataclasses.dataclass
class DestinyNoOauthNeeded(BaseBackendConnection):
    """ All functions here do not require any collected data and are access through the bungie api in the backend """

    destiny_id: int
    system: int

    async def get_destiny_name(
        self
    ) -> Optional[str]:
        """ Returns the name visible in destiny """

        # todo
        return None
