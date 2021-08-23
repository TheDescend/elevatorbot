import discord
from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from ElevatorBot.commandHelpers.optionTemplates import get_user_option
from ElevatorBot.misc.formating import embed_message


class DiscordJoinDate(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="discordjoindate",
        description="Check when you joined this discord server",
        options=[get_user_option()],
    )
    async def _discord_join_date(self, ctx: SlashContext, user: discord.Member):
        """Check your join date of this discord server"""

        await ctx.send(
            embed=embed_message(
                f"{user.display_name}'s Discord Join Date",
                f"You joined on <t:{int(user.joined_at.timestamp())}>",
            )
        )


def setup(client):
    client.add_cog(DiscordJoinDate(client))
