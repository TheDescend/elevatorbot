from dis_snek.errors import Forbidden
from dis_snek.models import Guild, GuildText

from settings import (
    DESCEND_CHANNEL_ADMIN_ID,
    DESCEND_CHANNEL_BOT_DEV_ID,
    DESCEND_CHANNEL_COMMUNITY_ROLES_ID,
    DESCEND_CHANNEL_JOIN_LOG_ID,
    DESCEND_CHANNEL_REGISTRATION_ID,
    DESCEND_GUILD_ID,
)


class __DescendChannels:
    guild: Guild | int | None = DESCEND_GUILD_ID

    admin_channel: GuildText | int | None = DESCEND_CHANNEL_ADMIN_ID
    bot_dev_channel: GuildText | int | None = DESCEND_CHANNEL_BOT_DEV_ID
    registration_channel: GuildText | int | None = DESCEND_CHANNEL_REGISTRATION_ID
    community_roles_channel: GuildText | int | None = DESCEND_CHANNEL_COMMUNITY_ROLES_ID
    join_log_channel: GuildText | int | None = DESCEND_CHANNEL_JOIN_LOG_ID

    async def init_channels(self, client):
        """Runs on startup to get the channels we use"""
        try:
            self.guild = await client.get_guild(self.guild)
        except Forbidden:
            # loop through all class attributes and set them to None
            for attr, value in self.__dict__.items():
                setattr(self, attr, None)
            return False

        # loop through all class attributes and fill out the channel objs
        for attr, value in self.__dict__.items():
            # get the channel
            channel = await self.guild.fetch_channel(value)
            setattr(self, attr, channel)
        return True


descend_channels: __DescendChannels = __DescendChannels()
