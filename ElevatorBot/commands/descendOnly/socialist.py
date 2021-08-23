from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from ElevatorBot.commandHelpers.permissionTemplates import permissions_socialist


class Socialist(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="socialist",
        description="Spams #socialist",
        default_permission=False,
        permissions=permissions_socialist,
    )
    async def _socialist(self, ctx: SlashContext):
        """Spams #socialist"""

        await ctx.send("No 🙃")


def setup(client):
    client.add_cog(Socialist(client))
