import dataclasses

from Backend.database.models import DiscordUsers, Roles


@dataclasses.dataclass
class Cache:
    # User Object - Key: discord_id
    discord_users: dict[int, DiscordUsers] = dataclasses.field(init=False, default_factory=dict)

    # Roles Object - Key: role_id
    roles: dict[int, Roles] = dataclasses.field(init=False, default_factory=dict)

    # Guild Roles Object - Key: guild_id
    guild_roles: dict[int, list[Roles]] = dataclasses.field(init=False, default_factory=dict)


cache = Cache()
