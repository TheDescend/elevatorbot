import dataclasses
from typing import Optional

from dis_snek.models import Guild, GuildVoice, Role, ThreadChannel

from ElevatorBot.core.misc.persistentMessages import PersistentMessages


@dataclasses.dataclass
class ReplyCache:
    """This saves the user_id and thread to prevent the same user from opening new threads all the time"""

    user_to_thread: dict[int, ThreadChannel] = dataclasses.field(init=False, default_factory=dict)
    thread_to_user: dict[ThreadChannel, int] = dataclasses.field(init=False, default_factory=dict)


@dataclasses.dataclass
class RegisteredRoleCache:
    """This saves registered data (for each guild) in the cache"""

    guild_to_role: dict[int, Role] = dataclasses.field(init=False, default_factory=dict)
    not_registered_users: list[int] = dataclasses.field(init=False, default_factory=list)

    async def get(self, guild: Guild) -> Optional[Role]:
        """Get the role for a guild"""

        if guild.id not in self.guild_to_role:
            persistent_messages = PersistentMessages(ctx=None, guild=guild, message_name="registered_role")
            result = await persistent_messages.get()

            if not result:
                return

            role = await guild.get_role(result.channel_id)
            if not role:
                return

            self.guild_to_role.update({guild.id: role})

        return self.guild_to_role[guild.id]

    async def is_not_registered(self, user_id: int) -> bool:
        """Returns True if the user is not registered and that is cached. False if we dont know"""

        return user_id in self.not_registered_users


@dataclasses.dataclass
class DescendCache:
    """This saves descend only info"""

    booster_count_channel: GuildVoice = dataclasses.field(init=False, default=None)
    member_count_channel: GuildVoice = dataclasses.field(init=False, default=None)

    async def get_booster_count(self, descend_guild: Guild) -> GuildVoice:
        """Get the booster count channel"""

        if not self.booster_count_channel:
            # populate it
            persistent_messages = PersistentMessages(ctx=None, guild=descend_guild, message_name="booster_count")
            result = await persistent_messages.get()

            if not result:
                raise LookupError("There is no channel set")

            self.booster_count_channel = await descend_guild.get_channel(result.channel_id)

        return self.booster_count_channel

    async def get_member_count(self, descend_guild: Guild) -> GuildVoice:
        """Get the member count channel"""

        if not self.member_count_channel:
            # populate it
            persistent_messages = PersistentMessages(ctx=None, guild=descend_guild, message_name="member_count")
            result = await persistent_messages.get()

            if not result:
                raise LookupError("There is no channel set")

            self.member_count_channel = await descend_guild.get_channel(result.channel_id)

        return self.member_count_channel


reply_cache = ReplyCache()
registered_role_cache = RegisteredRoleCache()
descend_cache = DescendCache()
