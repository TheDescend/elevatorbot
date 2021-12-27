import dataclasses
import datetime
from typing import Optional

from dis_snek.models import Guild

from DestinyEnums.enums import UsableDestinyActivityModeTypeEnum
from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.routes import (
    destiny_account_artifact_level_route,
    destiny_account_bright_dust_route,
    destiny_account_catalysts_route,
    destiny_account_characters_route,
    destiny_account_collectible_route,
    destiny_account_consumable_amount_route,
    destiny_account_leg_shards_route,
    destiny_account_max_power_route,
    destiny_account_metric_route,
    destiny_account_name_route,
    destiny_account_seals_route,
    destiny_account_season_pass_level_route,
    destiny_account_seasonal_challenges_route,
    destiny_account_solos_route,
    destiny_account_stat_characters_route,
    destiny_account_stat_route,
    destiny_account_time_route,
    destiny_account_triumph_route,
    destiny_account_triumph_score_route,
    destiny_account_vault_space_route,
)
from NetworkingSchemas.basic import BoolModel, NameModel, ValueModel
from NetworkingSchemas.destiny.account import (
    BoolModelRecord,
    DestinyCatalystsModel,
    DestinyCharactersModel,
    DestinyLowMansModel,
    DestinySealsModel,
    DestinyStatInputModel,
    DestinyTimesModel,
    DestinyTriumphScoreModel,
    SeasonalChallengesModel,
)


@dataclasses.dataclass
class DestinyAccount(BaseBackendConnection):

    discord_guild: Guild

    async def get_destiny_name(self) -> NameModel:
        """Return the destiny name"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_name_route.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id),
        )

        # convert to correct pydantic model
        return NameModel.parse_obj(result.result)

    async def get_solos(self) -> DestinyLowMansModel:
        """Return the solos the user has done"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_solos_route.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id),
        )

        # convert to correct pydantic model
        return DestinyLowMansModel.parse_obj(result.result)

    async def get_time(
        self,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        modes: Optional[list[UsableDestinyActivityModeTypeEnum]] = None,
        activity_ids: Optional[list[int]] = None,
        character_class: Optional[str] = None,
    ) -> DestinyTimesModel:
        """Return the time played for the given period"""

        if modes is None:
            modes = [UsableDestinyActivityModeTypeEnum.ALL]
        # todo pydantic model
        result = await self._backend_request(
            method="POST",
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
        return DestinyTimesModel.parse_obj(result.result)

    async def get_character_info(self) -> DestinyCharactersModel:
        """Return the character info"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_characters_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

        # convert to correct pydantic model
        return DestinyCharactersModel.parse_obj(result.result)

    async def has_collectible(self, collectible_id: int) -> BoolModel:
        """Return if the collectible is had"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_collectible_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id, collectible_id=collectible_id
            ),
        )

        # convert to correct pydantic model
        return BoolModel.parse_obj(result.result)

    async def has_triumph(self, triumph_id: int) -> BoolModelRecord:
        """Return if the triumph is had"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_triumph_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id, triumph_id=triumph_id
            ),
        )

        # convert to correct pydantic model
        return BoolModelRecord.parse_obj(result.result)

    async def get_metric(self, metric_id: int) -> ValueModel:
        """Return the metric value"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_metric_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id, metric_id=metric_id
            ),
        )

        # convert to correct pydantic model
        return ValueModel.parse_obj(result.result)

    async def get_stat(self, stat_name: str, stat_category: str = "allTime") -> ValueModel:
        """Return the stat value"""

        result = await self._backend_request(
            method="POST",
            route=destiny_account_stat_route.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id),
            data=DestinyStatInputModel(stat_category=stat_category, stat_name=stat_name),
        )

        # convert to correct pydantic model
        return ValueModel.parse_obj(result.result)

    async def get_stat_by_characters(
        self, character_id: int, stat_name: str, stat_category: str = "allTime"
    ) -> ValueModel:
        """Return the stat value by character"""

        result = await self._backend_request(
            method="POST",
            route=destiny_account_stat_characters_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id, character_id=character_id
            ),
            data=DestinyStatInputModel(stat_category=stat_category, stat_name=stat_name),
        )

        # convert to correct pydantic model
        return ValueModel.parse_obj(result.result)

    async def get_seasonal_challenges(self) -> SeasonalChallengesModel:
        """Return the seasonal challenges"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_seasonal_challenges_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

        # convert to correct pydantic model
        return SeasonalChallengesModel.parse_obj(result.result)

    async def get_triumph_score(self) -> DestinyTriumphScoreModel:
        """Return the user's triumph scores"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_triumph_score_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

        # convert to correct pydantic model
        return DestinyTriumphScoreModel.parse_obj(result.result)

    async def get_artifact_level(self) -> ValueModel:
        """Return the user's artifact_level"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_artifact_level_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

        # convert to correct pydantic model
        return ValueModel.parse_obj(result.result)

    async def get_season_pass_level(self) -> ValueModel:
        """Return the user's season_pass_level"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_season_pass_level_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

        # convert to correct pydantic model
        return ValueModel.parse_obj(result.result)

    async def get_consumable_amount(self, consumable_id: int) -> ValueModel:
        """Return the user's consumable amount"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_consumable_amount_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id, consumable_id=consumable_id
            ),
        )

        # convert to correct pydantic model
        return ValueModel.parse_obj(result.result)

    async def get_max_power(self) -> ValueModel:
        """Return the user's max power"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_max_power_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

        # convert to correct pydantic model
        return ValueModel.parse_obj(result.result)

    async def get_vault_space(self) -> ValueModel:
        """Return the user's vault space used"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_vault_space_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

        # convert to correct pydantic model
        return ValueModel.parse_obj(result.result)

    async def get_bright_dust(self) -> ValueModel:
        """Return the user's bright dust"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_bright_dust_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

        # convert to correct pydantic model
        return ValueModel.parse_obj(result.result)

    async def get_leg_shards(self) -> ValueModel:
        """Return the user's legendary shards"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_leg_shards_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

        # convert to correct pydantic model
        return ValueModel.parse_obj(result.result)

    async def get_catalyst_completion(self) -> DestinyCatalystsModel:
        """Gets all catalysts and the users completion status"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_catalysts_route.format(
                guild_id=self.discord_guild.id, discord_id=self.discord_member.id
            ),
        )

        # convert to correct pydantic model
        return DestinyCatalystsModel.parse_obj(result.result)

    async def get_seal_completion(self) -> DestinySealsModel:
        """Gets all seals and the users completion status"""

        result = await self._backend_request(
            method="GET",
            route=destiny_account_seals_route.format(guild_id=self.discord_guild.id, discord_id=self.discord_member.id),
        )

        # convert to correct pydantic model
        return DestinySealsModel.parse_obj(result.result)
