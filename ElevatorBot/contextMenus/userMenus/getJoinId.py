from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.context import MenuContext
from discord_slash.model import ButtonStyle, ContextMenuType
from discord_slash.utils import manage_components

from ElevatorBot.core.destiny.profile import DestinyProfile
from ElevatorBot.misc.formating import embed_message


class UserMenuCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_context_menu(target=ContextMenuType.USER, name="Get Join Code", guild_ids=[280456587464933376])
    async def get_join_id(self, ctx: MenuContext):
        destiny_profile = DestinyProfile(client=ctx.bot, discord_member=ctx.target_author, discord_guild=ctx.guild)
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
                hidden=True,
                embed=embed_message(
                    f"{ctx.target_author.display_name}'s Join Code",
                    f"`/join {result.result['join_id']}`",
                ),
                components=components,
            )


def setup(client):
    client.add_cog(UserMenuCommands(client))
