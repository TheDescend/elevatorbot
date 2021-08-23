from discord.ext.commands import Cog
from discord_slash import ButtonStyle, SlashContext, cog_ext
from discord_slash.utils import manage_components

from ElevatorBot.misc.formating import embed_message
from settings import BUNGIE_OAUTH


class Register(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="register",
        description="Link your Destiny 2 account with ElevatorBot",
    )
    async def _register(self, ctx: SlashContext):
        """Link your Destiny 2 account with ElevatorBot"""

        # not in dms
        if not ctx.guild:
            await ctx.send("Error" "Please use this command in your clans bot-channel")
            return

        # send the link to click on in a hidden embed
        components = [
            manage_components.create_actionrow(
                manage_components.create_button(
                    style=ButtonStyle.URL,
                    label=f"Registration Link",
                    url=f"""https://www.bungie.net/en/oauth/authorize?client_id={BUNGIE_OAUTH}&response_type=code&state={f"{ctx.author.id}:{ctx.guild.id}:{ctx.channel.id}"}""",
                ),
            ),
        ]

        await ctx.send(
            hidden=True,
            components=components,
            embed=embed_message(
                f"Registration",
                f"Use the button below to register with me",
                "Please be aware that I will need a while to process your data after you register for the first time, so I might react very slowly to your first commands.",
            ),
        )


def setup(client):
    client.add_cog(Register(client))
