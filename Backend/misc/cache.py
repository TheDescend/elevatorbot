import dataclasses
import datetime
from typing import Optional

from Backend.database.models import DiscordUsers, PersistentMessage, Roles


@dataclasses.dataclass
class Cache:
    # Saved PGCR IDs - Key: instance_id
    saved_pgcrs: set[int] = dataclasses.field(init=False, default_factory=set)
    updater_instances: dict[int, datetime.datetime] = dataclasses.field(init=False, default_factory=dict)
    updater_running_updates: set[int] = dataclasses.field(init=False, default_factory=set)

    # User Objects - Key: discord_id
    discord_users: dict[int, DiscordUsers] = dataclasses.field(init=False, default_factory=dict)
    # Key: destiny_id
    discord_users_by_destiny_id: dict[int, DiscordUsers] = dataclasses.field(init=False, default_factory=dict)

    # Role Objects - Key: role_id
    roles: dict[int, Roles] = dataclasses.field(init=False, default_factory=dict)

    # Guild Roles Objects - Key: guild_id
    guild_roles: dict[int, list[Roles]] = dataclasses.field(init=False, default_factory=dict)

    # Persistent Messages Objects - Key: f"{guild_id}|{message_name}"
    persistent_messages: dict[str, Optional[PersistentMessage]] = dataclasses.field(init=False, default_factory=dict)

    # User Triumphs - Key: destiny_id[triumph_hash]
    triumphs: dict[int, set[int]] = dataclasses.field(init=False, default_factory=dict)

    # User Collectibles - Key: destiny_id[collectible_hash]
    collectibles: dict[int, set[int]] = dataclasses.field(init=False, default_factory=dict)


cache = Cache()
