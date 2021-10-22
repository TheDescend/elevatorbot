from dis_snek.client import Snake
from dis_snek.models import InteractionContext, Scale

from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile


class BaseScale(Scale):
    """Add checks to every scale"""

    def __init__(self, client):
        self.client: Snake = client
        self.add_scale_check(self.registered_check)

    @staticmethod
    async def registered_check(ctx: InteractionContext) -> bool:
        """
        Default command that is run before the command is handled
        Checks if the command invoker is registered
        """

        # todo test
        return await DestinyProfile(client=ctx.bot, discord_member=ctx.author, discord_guild=ctx.guild).has_token()
