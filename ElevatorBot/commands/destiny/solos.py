import discord
from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from ElevatorBot.commandHelpers.optionTemplates import get_user_option
from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.misc.formating import embed_message


class Solos(Cog):
    """Shows you an overview of your Destiny 2 solo activity completions"""

    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="solos",
        description="Shows you an overview of your Destiny 2 solo activity completions",
        options=[get_user_option()],
    )
    async def _solos(self, ctx: SlashContext, user: discord.Member):

        await ctx.defer()
        account = DestinyAccount(client=ctx.bot, discord_member=user, discord_guild=ctx.guild)

        # get the solo data
        solos = await account.get_solos()
        if not solos:
            await solos.send_error_message(ctx=ctx)
            return

        # start building the return embed
        embed = embed_message(f"{user.display_name}'s Destiny Solos")

        # add the fields
        for solo_data in solos.result["solos"]:
            embed.add_field(
                name=solo_data["activity_name"],
                value=f"""Solo Completions: **{solo_data["count"]}**\nSolo Flawless Count: **{solo_data["flawless_count"]}**\nFastest Solo: **{solo_data["fastest"]}**""",
                inline=True,
            )

        # add a pity description
        if not solos.result["solos"]:
            embed.description = "You do not seem to have any notable solo completions"

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Solos(client))
