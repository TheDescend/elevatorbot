import dataclasses
from typing import Optional

from Backend.database.models import (
    DestinyInventoryItemDefinition,
    DestinyPresentationNodeDefinition,
    DestinyRecordDefinition,
    DestinySeasonPassDefinition,
    DiscordUsers,
    PersistentMessage,
)
from Shared.networkingSchemas.destiny import DestinyActivityModel, SeasonalChallengesModel
from Shared.networkingSchemas.destiny.roles import RoleModel


@dataclasses.dataclass
class Cache:
    # Saved PGCR IDs - Key: instance_id
    saved_pgcrs: set[int] = dataclasses.field(init=False, default_factory=set)

    # User Objects - Key: discord_id
    discord_users: dict[int, DiscordUsers] = dataclasses.field(init=False, default_factory=dict)

    # Role Objects - Key: role_id
    roles: dict[int, RoleModel] = dataclasses.field(init=False, default_factory=dict)

    # Guild Roles Objects - Key: guild_id
    guild_roles: dict[int, list[RoleModel]] = dataclasses.field(init=False, default_factory=dict)

    # Persistent Messages Objects - Key: f"{guild_id}|{message_name}"
    persistent_messages: dict[str, Optional[PersistentMessage]] = dataclasses.field(init=False, default_factory=dict)

    # User Triumphs - Key: destiny_id[triumph_hash]
    triumphs: dict[int, dict[int, bool]] = dataclasses.field(init=False, default_factory=dict)

    # User Collectibles - Key: destiny_id[collectible_hash]
    collectibles: dict[int, dict[int, bool]] = dataclasses.field(init=False, default_factory=dict)

    # Manifest Definitions. Saving DB calls since 1982. Make sure to `async with asyncio.Lock():` them
    season_pass_definition: Optional[DestinySeasonPassDefinition] = dataclasses.field(init=False, default=None)
    seasonal_challenges_definition: Optional[SeasonalChallengesModel] = dataclasses.field(init=False, default=None)

    # Inventory Items  - Key: reference_id
    items: dict[int, Optional[DestinyInventoryItemDefinition]] = dataclasses.field(init=False, default_factory=dict)

    # Catalysts
    catalysts: list[DestinyRecordDefinition] = dataclasses.field(init=False, default_factory=list)

    # Seals
    seals: dict[DestinyPresentationNodeDefinition, list[DestinyRecordDefinition]] = dataclasses.field(
        init=False, default_factory=dict
    )

    # Interesting Solos - Key: activity_category
    interesting_solos: dict[str, list[DestinyActivityModel]] = dataclasses.field(init=False, default_factory=dict)

    def reset(self):
        """Reset the caches after a manifest update"""

        self.season_pass_definition = None
        self.seasonal_challenges_definition = None
        self.items = {}
        self.catalysts = []
        self.seals = {}
        self.interesting_solos = {}


cache = Cache()
