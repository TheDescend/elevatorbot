import dataclasses
import datetime
from typing import Optional

from dis_snek.client import Snake
from dis_snek.models import Guild

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.backendNetworking.routes import (
    destiny_account_characters_route,
    destiny_account_collectible_route,
    destiny_account_metric_route,
    destiny_account_name_route,
    destiny_account_seasonal_challenges_route,
    destiny_account_solos_route,
    destiny_account_stat_characters_route,
    destiny_account_stat_route,
    destiny_account_time_route,
    destiny_account_triumph_route,
)
from ElevatorBot.static.destinyEnums import ModeScope
from NetworkingSchemas.destiny.account import (
    BoolModel,
    DestinyCharactersModel,
    DestinyLowMansModel,
    DestinyNameModel,
    DestinyStatModel,
    DestinyTimeModel,
    SeasonalChallengesModel,
)


@dataclasses.dataclass
class DestinyAccount(BaseBackendConnection):
    client: Snake
    discord_guild: Guild

    async def get_destiny_name(self) -> Optional[DestinyNameModel]:
        """Return the destiny name"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_name_route.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id),
        )

        # convert to correct pydantic model
        return DestinyNameModel.parse_obj(result.result) if result else None

    async def get_solos(self) -> Optional[DestinyLowMansModel]:
        """Return the solos the user has done"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_solos_route.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id),
        )

        # convert to correct pydantic model
        return DestinyLowMansModel.parse_obj(result.result) if result else None

    async def get_time(
        self,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        modes: Optional[list[ModeScope]] = None,
        activity_ids: Optional[list[int]] = None,
        character_class: Optional[str] = None,
    ) -> Optional[DestinyTimeModel]:
        """Return the time played for the given period"""

        if modes is None:
            modes = [ModeScope.ALL]

        result = await self._backend_request(
            method="GET",
            route=destiny_account_time_route.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id),
            data={
                "start_time": start_time,
                "end_time": end_time,
                "mode": [mode.value for mode in modes],
                "activity_ids": activity_ids,
                "character_class": character_class,
            },
        )

        # convert to correct pydantic model
        return DestinyTimeModel.parse_obj(result.result) if result else None

    async def get_character_info(self) -> Optional[DestinyCharactersModel]:
        """Return the character info"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_characters_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

        # convert to correct pydantic model
        return DestinyCharactersModel.parse_obj(result.result) if result else None

    async def has_collectible(self, collectible_id: int) -> Optional[BoolModel]:
        """Return if the collectible is had"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_collectible_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id, collectible_id=collectible_id
            ),
        )

        # convert to correct pydantic model
        return BoolModel.parse_obj(result.result) if result else None

    async def has_triumph(self, triumph_id: int) -> Optional[BoolModel]:
        """Return if the triumph is had"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_triumph_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id, triumph_id=triumph_id
            ),
        )

        # convert to correct pydantic model
        return BoolModel.parse_obj(result.result) if result else None

    async def get_metric(self, metric_id: int) -> Optional[DestinyStatModel]:
        """Return the metric value"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_metric_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id, metric_id=metric_id
            ),
        )

        # convert to correct pydantic model
        return DestinyStatModel.parse_obj(result.result) if result else None

    async def get_stat(self, stat_name: str, stat_category: str = "allTime") -> Optional[DestinyStatModel]:
        """Return the stat value"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_stat_route.format(
                guild_id=self.discord_guild.id,
                discord_id=self.discord_member.id,
                stat_category=stat_category,
                stat_name=stat_name,
            ),
        )

        # convert to correct pydantic model
        return DestinyStatModel.parse_obj(result.result) if result else None

    async def get_stat_by_characters(
        self, character_id: int, stat_name: str, stat_category: str = "allTime"
    ) -> Optional[DestinyStatModel]:
        """Return the stat value by character"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_stat_characters_route.format(
                guild_id=self.discord_guild.id,
                discord_id=self.discord_member.id,
                character_id=character_id,
                stat_category=stat_category,
                stat_name=stat_name,
            ),
        )

        # convert to correct pydantic model
        return DestinyStatModel.parse_obj(result.result) if result else None

    async def get_seasonal_challenges(self) -> Optional[SeasonalChallengesModel]:
        """Return the seasonal challenges"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_seasonal_challenges_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

        # convert to correct pydantic model
        return SeasonalChallengesModel.parse_obj(result.result) if result else None
