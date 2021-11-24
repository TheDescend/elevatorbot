from dis_snek import Snake
from dis_snek.models import Guild, GuildText

descend_filler_role_ids = [670395920327639085, 670385837044662285, 670385313994113025, 776854211585376296]

descend_muted_role_id = 681944329698541585
descend_no_nickname_role_id = 887021717053124659
descend_muted_ids = {descend_muted_role_id: "Muted", descend_no_nickname_role_id: "Muted - No Nickname"}


class __DescendChannels:
    guild: Guild | int = 669293365900214293

    admin_channel: GuildText | int = 669293365900214293
    bot_dev_channel: GuildText | int = 670570955290181675
    registration_channel: GuildText | int = 769612069581881434
    community_roles_channel: GuildText | int = 686568386590802000
    join_log_channel: GuildText | int = 669293365900214298

    async def init_channels(self, client: Snake):
        """Runs on startup to get the channels we use"""

        self.guild = await client.get_guild(self.guild)

        # loop through all class attributes
        for attr, value in self.__dict__.items():
            # get the channel
            channel = await self.guild.get_channel(value)
            setattr(self, attr, channel)


descend_channels: __DescendChannels = __DescendChannels()
