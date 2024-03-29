from naff import slash_command

from ElevatorBot.commandHelpers.permissionTemplates import restrict_default_permission
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.destiny.profile import DestinyProfile
from Shared.functions.readSettingsFile import get_setting

# =============
# Descend Only!
# =============


class ApiKey(BaseModule):
    @slash_command(
        name="api_key", description="Get your own Destiny 2 oauth api key", scopes=get_setting("COMMAND_GUILD_SCOPE")
    )
    @restrict_default_permission()
    async def api_key(self, ctx: ElevatorInteractionContext):
        token = await DestinyProfile(ctx=ctx, discord_member=ctx.author, discord_guild=ctx.guild).has_token()

        await ctx.send(embeds=embed_message("Token", f"`Bearer {token.value}`", member=ctx.author), ephemeral=True)


def setup(client):
    ApiKey(client)
