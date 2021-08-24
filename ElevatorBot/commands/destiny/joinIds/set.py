from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

from ElevatorBot.commandHelpers.optionTemplates import get_user_option
from ElevatorBot.core.destiny.profile import DestinyProfile
from ElevatorBot.misc.formating import embed_message


class IdSet(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_subcommand(
        base="id",
        base_description="Steam IDs which can be used to join people in Destiny 2 without adding them as a friend",
        name="set",
        description="Set / Update your Steam ID",
        options=[
            create_option(
                name="steamid",
                description="Your Steam ID",
                option_type=3,
                required=True,
            ),
        ],
    )
    async def _set(self, ctx: SlashContext, steamid: int):
        """Set / Update your Steam ID"""

        destiny_profile = DestinyProfile(client=ctx.bot, discord_member=ctx.author, discord_guild=ctx.guild)
        result = await destiny_profile.update_join_id(steamid)

        if not result:
            await result.send_error_message(ctx, hidden=True)
        else:
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    f"Success",
                    f"Your Join Code has been update to \n`/join {result.result['join_id']}`",
                ),
            )


def setup(client):
    client.add_cog(IdSet(client))
