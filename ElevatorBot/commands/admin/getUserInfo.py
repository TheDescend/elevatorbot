from discord.ext.commands import Cog
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

from ElevatorBot.commandHelpers.permissionTemplates import permissions_admin


class UserInfo(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


@cog_ext.cog_slash(
    name="userinfo",
    description="Gets collected info for the specified user",
    options=[
        create_option(
            name="discorduser",
            description="Look up a discord user",
            option_type=6,
            required=False,
        ),
        create_option(
            name="destinyid",
            description="Look up a destinyID",
            option_type=3,
            required=False,
        ),
        create_option(
            name="fuzzyname",
            description="If you know how the user is called",
            option_type=3,
            required=False,
        ),
    ],
    default_permission=False,
    permissions=permissions_admin,
)
async def _userinfo():
    pass


def setup(
    client
):
    client.add_cog(UserInfo(client))
