from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

from ElevatorBot.commandHelpers.optionTemplates import get_user_option
from ElevatorBot.commandHelpers.permissionTemplates import permissions_admin


class Reply(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="reply",
        description="Send a message to whoever got tagged above",
        options=[
            create_option(
                name="message",
                description="What message to reply with",
                option_type=3,
                required=True,
            ),
            get_user_option("Which user to reply to"),
        ],
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _reply(self, ctx: SlashContext, message: str, user=None):
        pass


def setup(client):
    client.add_cog(Reply(client))
