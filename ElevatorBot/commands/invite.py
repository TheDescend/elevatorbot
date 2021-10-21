from dis_snek.models import InteractionContext, slash_command

from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message


class Invite(BaseScale):
    @slash_command(name="invite", description="Sends you the invite link to add me to your own server")
    async def _invite(self, ctx: InteractionContext):
        invite_link = "https://discord.com/api/oauth2/authorize?client_id=847935658072604712&permissions=536299961937&scope=bot%20applications.commands"
        await ctx.send(
            ephemeral=True,
            embeds=embed_message("Invite Link", f"Click [here]({invite_link}) to invite me to another server"),
        )


def setup(client):
    Invite(client)
