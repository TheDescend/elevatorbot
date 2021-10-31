import dataclasses

from dis_snek.models import Guild, Role, ThreadChannel

from ElevatorBot.core.misc.persistentMessages import PersistentMessages


@dataclasses.dataclass
class ReplyCache:
    """This saves the user_id and thread to prevent the same user from opening new threads all the time"""

    user_to_thread: dict[int, ThreadChannel] = dataclasses.field(init=False, default_factory=dict)
    thread_to_user: dict[ThreadChannel, int] = dataclasses.field(init=False, default_factory=dict)


@dataclasses.dataclass
class RegisteredRoleCache:
    """This saves the registered role for each guild in the cache"""

    _guild_to_role: dict[int, Role] = dataclasses.field(init=False, default_factory=dict)

    async def get(self, guild: Guild) -> Role:
        """Get the role for a guild"""

        if guild.id not in self._guild_to_role:
            persistent_messages = PersistentMessages(guild=guild, message_name="registered_role")
            result = await persistent_messages.get()

            self._guild_to_role.update({guild.id: result.result["channel_id"]})
        return self._guild_to_role[guild.id]


reply_cache = ReplyCache()
registered_role_cache = RegisteredRoleCache()
