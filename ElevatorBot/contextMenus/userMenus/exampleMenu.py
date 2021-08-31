from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.context import MenuContext
from discord_slash.model import ContextMenuType


class UserMenuCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_context_menu(target=ContextMenuType.USER, name="Ping Me", guild_ids=[280456587464933376])
    async def command(self, ctx: MenuContext):
        # just repeat the original message
        await ctx.send(ctx.target_author.mention)


def setup(client):
    client.add_cog(UserMenuCommands(client))
