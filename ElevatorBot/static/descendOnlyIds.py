from dis_snek.models import Guild, GuildText
from dis_snek.errors import Forbidden


descend_filler_role_ids = [670395920327639085, 670385837044662285, 670385313994113025, 776854211585376296]

descend_muted_role_id = 681944329698541585
descend_no_nickname_role_id = 887021717053124659
descend_muted_ids = {descend_muted_role_id: "Muted", descend_no_nickname_role_id: "Muted - No Nickname"}


class __DescendChannels:
    guild: Guild | int = 669293365900214293

    admin_channel: GuildText | int = 671264040974024705
    bot_dev_channel: GuildText | int = 670570955290181675
    registration_channel: GuildText | int = 769612069581881434
    community_roles_channel: GuildText | int = 686568386590802000
    join_log_channel: GuildText | int = 669293365900214298

    async def init_channels(self, client):
        """Runs on startup to get the channels we use"""
        try:
            self.guild = await client.get_guild(self.guild)
        except Forbidden:
            self.guild = None
            self.admin_channel = -1
            self.bot_dev_channel = -1
            self.registration_channel = -1
            self.community_roles_channel = -1
            self.join_log_channel = -1
            return False
        # loop through all class attributes
        for attr, value in self.__dict__.items():
            # get the channel
            channel = await self.guild.get_channel(value)
            setattr(self, attr, channel)
        return True


descend_channels: __DescendChannels = __DescendChannels()
