from dis_snek.models import InteractionContext, slash_command

from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message
from settings import COMMAND_GUILD_SCOPE


class ApiKey(BaseScale):

    # todo perm
    @slash_command(name="get_api_key", description="Get your own Destiny 2 oauth api key", scopes=COMMAND_GUILD_SCOPE)
    async def _get_api_key(self, ctx: InteractionContext):
        token = await DestinyProfile(ctx=ctx, discord_member=ctx.author, discord_guild=ctx.guild).has_token()

        await ctx.send(embeds=embed_message(f"Your Token", f"`Bearer {token.value}`"), ephemeral=True)


def setup(client):
    ApiKey(client)
