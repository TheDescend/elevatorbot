from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.context import MenuContext
from discord_slash.model import ButtonStyle, ContextMenuType
from discord_slash.utils import manage_components

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.misc.formating import embed_message


class UserMenuCommands(commands.Cog):
    """
    Gets collected info for the specified user
    """

    def __init__(self, client):
        self.client = client

    @cog_ext.cog_context_menu(target=ContextMenuType.USER, name="Get Join Code")
    async def command(self, ctx: MenuContext):
        destiny_profile = DestinyAccount(client=ctx.bot, discord_member=ctx.target_author, discord_guild=ctx.guild)
        result = await destiny_profile.get_destiny_name()

        if not result:
            await result.send_error_message(ctx, hidden=True)
        else:
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    f"{ctx.target_author.display_name}'s Join Code",
                    f"`/join {result.result['name']}`",
                ),
            )


def setup(client):
    client.add_cog(UserMenuCommands(client))
