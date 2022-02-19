from dis_snek import Guild, GuildText
from dis_snek.client.errors import Forbidden

from ElevatorBot.discordEvents.base import ElevatorSnake
from Shared.functions.readSettingsFile import get_setting


class __DescendChannels:
    def __init__(self):
        self.guild_id: int = get_setting("DESCEND_GUILD_ID")
        self.guild: Guild | None = None

        self.admin_channel: GuildText | int | None = get_setting("DESCEND_CHANNEL_ADMIN_ID")
        self.bot_dev_channel: GuildText | int | None = get_setting("DESCEND_CHANNEL_BOT_DEV_ID")
        self.registration_channel: GuildText | int | None = get_setting("DESCEND_CHANNEL_REGISTRATION_ID")
        self.community_roles_channel: GuildText | int | None = get_setting("DESCEND_CHANNEL_COMMUNITY_ROLES_ID")
        self.join_log_channel: GuildText | int | None = get_setting("DESCEND_CHANNEL_JOIN_LOG_ID")

    async def init_channels(self, client: ElevatorSnake):
        """Runs on startup to get the channels we use"""
        try:
            if guild := client.get_guild(self.guild_id):
                self.guild = guild
                # loop through all class attributes and fill out the channel objs
                for attr, value in self.__dict__.items():
                    if attr != "guild":
                        # get the channel
                        channel = await client.get_channel(value)
                        setattr(self, attr, channel)
        except Forbidden:
            pass
        finally:
            # loop through all class attributes and set them to None
            for attr, value in self.__dict__.items():
                setattr(self, attr, None)
            return False
        return True


descend_channels: __DescendChannels = __DescendChannels()
