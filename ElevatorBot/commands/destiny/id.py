import discord
from discord.ext.commands import Cog
from discord_slash import ButtonStyle, SlashContext, cog_ext
from discord_slash.utils import manage_components

from ElevatorBot.commandHelpers.optionTemplates import get_user_option
from ElevatorBot.core.destiny.account import DestinyAccount
from ElevatorBot.core.destiny.profile import DestinyProfile
from ElevatorBot.misc.formating import embed_message


class IdGet(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="id",
        description="Get the users Bungie Name, which can be used to join people in Destiny 2 without adding them as a friend",
        options=[get_user_option()],
    )
    async def _id(self, ctx: SlashContext, user: discord.Member = None):
        """Get the users Bungie Name, which can be used to join people in Destiny 2 without adding them as a friend"""

        # assign user to be the mentioned user if applicable
        user = user if user else ctx.author

        destiny_profile = DestinyAccount(client=ctx.bot, discord_member=user, discord_guild=ctx.guild)
        result = await destiny_profile.get_destiny_name()

        if not result:
            await result.send_error_message(ctx, hidden=True)
        else:
            await ctx.send(
                embed=embed_message(
                    f"{user.display_name}'s Join Code",
                    f"`/join {result.result['name']}`",
                ),
            )


def setup(client):
    client.add_cog(IdGet(client))
