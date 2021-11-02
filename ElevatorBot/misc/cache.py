import dataclasses

from dis_snek.models import Guild, GuildVoice, Role, ThreadChannel

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


@dataclasses.dataclass
class DescendCache:
    """This saves descend only info"""

    booster_count_channel: GuildVoice = dataclasses.field(init=False, default=None)
    member_count_channel: GuildVoice = dataclasses.field(init=False, default=None)

    async def get_booster_count(self, descend_guild: Guild) -> GuildVoice:
        """Get the booster count channel"""

        if not self.booster_count_channel:
            # populate it
            persistent_messages = PersistentMessages(guild=descend_guild, message_name="booster_count")
            result = await persistent_messages.get()

            if not result:
                raise LookupError("There is no channel set")

            self.booster_count_channel = await descend_guild.get_channel(result.result["channel_id"])

        return self.booster_count_channel

    async def get_member_count(self, descend_guild: Guild) -> GuildVoice:
        """Get the member count channel"""

        if not self.member_count_channel:
            # populate it
            persistent_messages = PersistentMessages(guild=descend_guild, message_name="member_count")
            result = await persistent_messages.get()

            if not result:
                raise LookupError("There is no channel set")

            self.member_count_channel = await descend_guild.get_channel(result.result["channel_id"])

        return self.member_count_channel


reply_cache = ReplyCache()
registered_role_cache = RegisteredRoleCache()
descend_cache = DescendCache()
