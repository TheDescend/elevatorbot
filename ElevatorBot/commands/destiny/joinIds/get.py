import discord
from discord.ext.commands import Cog
from discord_slash import ButtonStyle, SlashContext, cog_ext
from discord_slash.utils import manage_components

from ElevatorBot.commandHelpers.optionTemplates import get_user_option
from ElevatorBot.core.destiny.profile import DestinyProfile
from ElevatorBot.misc.formating import embed_message


class IdGet(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_subcommand(
        base="id",
        base_description="Steam IDs which can be used to join people in Destiny 2 without adding them as a friend",
        name="get",
        description="Get a Steam ID",
        options=[get_user_option()],
    )
    async def _get(self, ctx: SlashContext, user: discord.Member = None):
        """Get a Steam ID"""

        # assign user to be the mentioned user if applicable
        user = user if user else ctx.author

        destiny_profile = DestinyProfile(client=ctx.bot, discord_member=user, discord_guild=ctx.guild)
        result = await destiny_profile.get_join_id()

        if not result:
            await result.send_error_message(ctx, hidden=True)
        else:
            components = [
                manage_components.create_actionrow(
                    manage_components.create_button(
                        style=ButtonStyle.URL,
                        label=f"Or click here to join them directly",
                        url=f"steam://rungame/1085660/{result.result['join_id']}",
                    ),
                ),
            ]
            await ctx.send(
                embed=embed_message(
                    f"{user.display_name}'s Join Code",
                    f"`/join {result.result['join_id']}`",
                ),
                components=components
            )



def setup(client):
    client.add_cog(IdGet(client))
