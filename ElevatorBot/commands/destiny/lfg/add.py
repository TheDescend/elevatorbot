import discord
from discord.ext.commands import Cog
from discord_slash import cog_ext
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option

from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.core.destiny.lfgSystem import LfgMessage
from ElevatorBot.misc.formating import embed_message


class LfgAdd(Cog):
    """This is so cool, it adds people into the main roster even if full"""

    def __init__(self, client):
        self.client = client

    @cog_ext.cog_subcommand(
        base="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        name="add",
        description="Add a user to an lfg event",
        options=[
            create_option(
                name="lfg_id",
                description="The lfg message id",
                option_type=4,
                required=True,
            ),
            default_user_option(description="The user you want to add", required=True),
        ],
    )
    async def _add(self, ctx: SlashContext, lfg_id: int, user: discord.Member):
        # get the message obj
        lfg_message = await LfgMessage.from_lfg_id(lfg_id=lfg_id, client=ctx.bot, guild=ctx.guild)

        # error if that is not an lfg message
        if type(lfg_message) is BackendResult:
            await lfg_message.send_error_message(ctx=ctx, hidden=True)
            return

        if await lfg_message.add_joined(user, force_into_joined=True):
            embed = embed_message(
                "Success",
                f"{user.display_name} has been added to the LFG post with the id `{lfg_id}`",
            )
        else:
            embed = embed_message(
                "Error",
                f"{user.display_name} could not be added to the LFG post with the id `{lfg_id}`, because they are already in it or they are blacklisted by the creator",
            )

        await ctx.send(hidden=True, embed=embed)


def setup(client):
    client.add_cog(LfgAdd(client))
