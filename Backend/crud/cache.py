import dataclasses

from Backend.database.models import DiscordUsers, PersistentMessage, Roles


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


cache = Cache()
