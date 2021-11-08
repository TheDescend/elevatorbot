import dataclasses
from typing import Optional

from Backend.database.models import (
    DestinySeasonPassDefinition,
    DiscordUsers,
    PersistentMessage,
    Roles,
)
from NetworkingSchemas.destiny.account import SeasonalChallengesModel


@dataclasses.dataclass
class Cache:
    # User Objects - Key: discord_id
    discord_users: dict[int, DiscordUsers] = dataclasses.field(init=False, default_factory=dict)

    # Roles Objects - Key: role_id
    roles: dict[int, Roles] = dataclasses.field(init=False, default_factory=dict)

    # Guild Roles Objects - Key: guild_id
    guild_roles: dict[int, list[Roles]] = dataclasses.field(init=False, default_factory=dict)

    # Persistent Messages Objects - Key: f"{guild_id}|{message_name}"
    persistent_messages: dict[str, PersistentMessage] = dataclasses.field(init=False, default_factory=dict)

    # Manifest Definitions. Saving DB calls since 1982. Make sure to `async with asyncio.Lock():` them
    season_pass_definition: Optional[DestinySeasonPassDefinition] = dataclasses.field(init=False, default=None)
    seasonal_challenges_definition: Optional[SeasonalChallengesModel] = dataclasses.field(init=False, default=None)


cache = Cache()
