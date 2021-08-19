from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

from ElevatorBot.commandHelpers.optionTemplates import get_user_option
from ElevatorBot.commandHelpers.permissionTemplates import permissions_admin


class Mute(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_slash(
        name="mute",
        description="Mutes specified user for specified time",
        options=[
            get_user_option(
                description="Which user to mute", required=True
            ),
            create_option(
                name="hours",
                description="How many hours to mute the user for",
                option_type=4,
                required=True,
            ),
        ],
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _mute(
        self,
        ctx: SlashContext,
        user,
        hours: int
    ):
        pass


def setup(
    client
):
    client.add_cog(Mute(client))
