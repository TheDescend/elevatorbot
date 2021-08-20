import discord

from ElevatorBot.core.http import BaseBackendConnection
from ElevatorBot.core.routes import destiny_profile_from_destiny_id_route, destiny_profile_from_discord_id_route


class DestinyProfile(BaseBackendConnection):
    """ Get Destiny Info for a discord id """

    def __init__(
        self,
        discord_member: discord.Member,
        discord_guild: discord.Guild,
        discord_channel: discord.GroupChannel
    ):
        super().__init__(
            discord_member,
            discord_guild,
            discord_channel
        )

        # define the used routes
        self.route = destiny_profile_from_discord_id_route.format(
            discord_id=discord_member.id
        )


    async def get_from_discord_id(
        self
    ):
        """ Get the profile """

        return self.backend_get(self.route)


    async def get_from_destiny_id(
        self,
        destiny_id: int
    ):
        """ Get the profile """

        return self.backend_get(destiny_profile_from_destiny_id_route.format(
            destiny_id=destiny_id
        ))


    async def edit(
        self
    ):
        """ Edit the profile """

        pass


    async def delete(
        self
    ):
        """ Delete the profile """

        pass
