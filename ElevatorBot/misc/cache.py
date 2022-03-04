import dataclasses
import datetime
from typing import Optional

from cachetools import TTLCache
from dis_snek import Guild, GuildVoice, Message, Role, ThreadChannel

from ElevatorBot.core.misc.persistentMessages import PersistentMessages
from ElevatorBot.networking.destiny.items import DestinyItems
from ElevatorBot.static.descendOnlyIds import descend_channels
from Shared.functions.helperFunctions import get_min_with_tz, get_now_with_tz


@dataclasses.dataclass
class ReplyCache:
    """This saves the user_id and thread to prevent the same user from opening new threads all the time"""

    user_to_thread: dict[int, ThreadChannel] = dataclasses.field(init=False, default_factory=dict)
    thread_to_user: dict[int, int] = dataclasses.field(init=False, default_factory=dict)

    thread_message_id_to_user_message: dict[int, Message] = dataclasses.field(init=False, default_factory=dict)
    user_message_id_to_thread_message: dict[int, Message] = dataclasses.field(init=False, default_factory=dict)


@dataclasses.dataclass
class RegisteredRoleCache:
    """This saves registered data (for each guild) in the cache"""

    guild_to_role: dict[int, Role] = dataclasses.field(init=False, default_factory=dict)
    not_registered_users: list[int] = dataclasses.field(init=False, default_factory=list)
    registered_users: TTLCache = TTLCache(ttl=3600, maxsize=10000)

    async def get(self, guild: Guild) -> Optional[Role]:
        """Get the role for a guild"""

        if guild.id not in self.guild_to_role:
            persistent_messages = PersistentMessages(ctx=None, guild=guild, message_name="registered_role")
            result = await persistent_messages.get()

            if not result:
                return

            role = await guild.fetch_role(result.channel_id)
            if not role:
                return

            self.guild_to_role.update({guild.id: role})

        return self.guild_to_role[guild.id]

    def is_not_registered(self, user_id: int) -> bool:
        """Returns True if the user is not registered and that is cached. False if we dont know"""

        return user_id in self.not_registered_users

    def is_registered(self, user_id: int) -> bool:
        """Returns True if the user has been registered within the last hour"""

        return bool(self.registered_users.get(user_id))


@dataclasses.dataclass
class DescendCache:
    """This saves descend only info"""

    status_message: Message = None

    booster_count_channel: GuildVoice = dataclasses.field(init=False, default=None)
    member_count_channel: GuildVoice = dataclasses.field(init=False, default=None)

    async def get_booster_count(self) -> GuildVoice:
        """Get the booster count channel"""

        if not self.booster_count_channel:
            # populate it
            persistent_messages = PersistentMessages(
                ctx=None, guild=descend_channels.guild, message_name="booster_count"
            )
            result = await persistent_messages.get()

            if not result:
                raise LookupError("There is no channel set")

            self.booster_count_channel = await descend_channels.guild.fetch_channel(result.channel_id)

        return self.booster_count_channel

    async def get_member_count(self) -> GuildVoice:
        """Get the member count channel"""

        if not self.member_count_channel:
            # populate it
            persistent_messages = PersistentMessages(
                ctx=None, guild=descend_channels.guild, message_name="member_count"
            )
            result = await persistent_messages.get()

            if not result:
                raise LookupError("There is no channel set")

            self.member_count_channel = await descend_channels.guild.fetch_channel(result.channel_id)

        return self.member_count_channel

    async def init_status_message(self):
        """Cache the message where the status updates are"""

        persistent_messages = PersistentMessages(ctx=None, guild=descend_channels.guild, message_name="status")
        result = await persistent_messages.get()
        if not result:
            # when we have not set a message yet
            return

        channel = await descend_channels.guild.fetch_channel(result.channel_id)
        self.status_message = await channel.fetch_message(result.message_id)


@dataclasses.dataclass
class IDtoNameBase:
    _id_to_name: dict[int, str] = dataclasses.field(init=False, default_factory=dict)


@dataclasses.dataclass
class CollectibleCache(IDtoNameBase):
    async def get_name(self, collectible_id: int) -> str:
        """Get the name of a collectible"""

        if collectible_id not in self._id_to_name:
            # populate it
            result = await DestinyItems(ctx=None, discord_member=None).get_collectible_name(
                collectible_id=collectible_id
            )
            if not result or not result.name:
                raise LookupError

            self._id_to_name[collectible_id] = result.name

        return self._id_to_name[collectible_id]


@dataclasses.dataclass
class TriumphCache(IDtoNameBase):
    async def get_name(self, triumph_id: int) -> str:
        """Get the name of a triumph"""

        if triumph_id not in self._id_to_name:
            # populate it
            result = await DestinyItems(ctx=None, discord_member=None).get_triumph_name(triumph_id=triumph_id)
            if not result or not result.name:
                raise LookupError

            self._id_to_name[triumph_id] = result.name

        return self._id_to_name[triumph_id]


@dataclasses.dataclass
class PopTimelineCache:
    """This saves the url in the cache for an hour"""

    _time: datetime.datetime = dataclasses.field(init=False, default=get_min_with_tz())
    _url: str = dataclasses.field(init=False, default=None)

    @property
    def url(self) -> Optional[str]:
        """Get the url if it is not an hour old else None"""

        if self._time + datetime.timedelta(hours=1) > get_now_with_tz():
            return self._url

    @url.setter
    def url(self, new_url: str):
        """Set the url"""

        self._url = new_url
        self._time = get_now_with_tz()


reply_cache = ReplyCache()
registered_role_cache = RegisteredRoleCache()
descend_cache = DescendCache()
collectible_cache = CollectibleCache()
triumph_cache = TriumphCache()
pop_timeline_cache = PopTimelineCache()
