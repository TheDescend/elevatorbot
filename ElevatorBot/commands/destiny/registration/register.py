from dis_snek.models import (
    ActionRow,
    Button,
    ButtonStyles,
    ComponentContext,
    InteractionContext,
    slash_command,
)

from ElevatorBot.commands.base import RegisteredScale
from ElevatorBot.misc.formating import embed_message
from settings import BUNGIE_APPLICATION_CLIENT_ID


class Register(RegisteredScale):
    @slash_command(name="register", description="Link your Destiny 2 account with ElevatorBot")
    async def register(self, ctx: InteractionContext):
        await send_registration(ctx)


async def send_registration(ctx: InteractionContext | ComponentContext):
    """Send the user the message"""

    # send the link to click on in a hidden embed
    components = [
        ActionRow(
            Button(
                style=ButtonStyles.URL,
                label="Registration Link",
                url=f"""https://www.bungie.net/en/oauth/authorize?client_id={BUNGIE_APPLICATION_CLIENT_ID}&response_type=code&state={f"{ctx.author.id}:{ctx.guild.id}:{ctx.channel.id}"}""",
            ),
        ),
    ]

    await ctx.send(
        ephemeral=True,
        components=components,
        embeds=embed_message(
            "Registration",
            "Use the button below to registration with me",
            "Please be aware that I will need a while to process your data after you registration for the first time, so I might react very slowly to your first commands.",
        ),
    )


def setup(client):
    Register(client)
