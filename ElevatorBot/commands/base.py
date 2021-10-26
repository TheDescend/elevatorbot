from dis_snek.client import Snake
from dis_snek.models import InteractionContext, Scale

from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile
from ElevatorBot.misc.formating import embed_message


class BaseScale(Scale):
    """Add checks to every scale"""

    def __init__(self, client):
        self.client: Snake = client
        self.add_scale_check(self.registered_check)
        self.add_scale_check(self.no_dm_check)

    @staticmethod
    async def registered_check(ctx: InteractionContext) -> bool:
        """
        Default command that is run before the command is handled
        Checks if the command invoker is registered
        """

        # todo test
        result = await DestinyProfile(client=ctx.bot, discord_member=ctx.author, discord_guild=ctx.guild).has_token()

        if not result:
            # send error message
            await ctx.send(
                embeds=embed_message(
                    "Registration Required",
                    "You are not worthy ... yet\nPlease `/register` with me, then you can use my commands",
                    "Note: Registration is only valid for a year, so you might need to re-register now",
                )
            )

        return result

    @staticmethod
    async def no_dm_check(ctx: InteractionContext) -> bool:
        """
        Default command that is run before the command is handled
        Checks that the command is not invoked in dms
        """

        return bool(ctx.guild)
