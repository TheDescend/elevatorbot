from dis_snek import InteractionContext, slash_command

from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formatting import embed_message
from Shared.functions.readSettingsFile import get_setting

# =============
# Descend Only!
# =============


class ApiKey(BaseScale):

    # todo perm
    @slash_command(
        name="api_key", description="Get your own Destiny 2 oauth api key", scopes=get_setting("COMMAND_GUILD_SCOPE")
    )
    async def api_key(self, ctx: InteractionContext):
        token = await DestinyProfile(ctx=ctx, discord_member=ctx.author, discord_guild=ctx.guild).has_token()

        await ctx.send(embeds=embed_message("Token", f"`Bearer {token.value}`", member=ctx.author), ephemeral=True)


def setup(client):
    ApiKey(client)
