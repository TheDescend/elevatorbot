from naff import Cog

from ElevatorBot.commandHelpers.responseTemplates import respond_pending
from ElevatorBot.discordEvents.base import ElevatorClient
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.cache import registered_role_cache
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.destiny.profile import DestinyProfile
from ElevatorBot.networking.errors import BackendException


class RegisteredModule(Cog):
    """Add checks to every module"""

    bot: ElevatorClient

    def __init__(self, client: ElevatorClient):
        self.client = client
        self.add_cog_check(self.no_dm_check)  # noqa
        self.add_cog_check(self.no_pending_check)  # noqa

    @staticmethod
    async def no_pending_check(ctx: ElevatorInteractionContext) -> bool:
        """
        Default command that is run before the command is handled
        Checks that the command is not invoked by pending members
        """

        if ctx.author.pending:
            await respond_pending(ctx)
            return False
        return True


class BaseModule(RegisteredModule):
    """Add a registered check to every module"""

    def __init__(self, client: ElevatorClient):
        self.add_cog_check(self.registered_check)  # noqa
        super().__init__(client)

    @staticmethod
    async def registered_check(ctx: ElevatorInteractionContext) -> bool:
        """
        Default command that is run before the command is handled
        Checks if the command invoker is registered
        """

        # this gets handled by the DM check
        if not ctx.guild:
            return True

        # get the registration role
        try:
            registration_role = await registered_role_cache.get(guild=ctx.guild)
        except BackendException:
            registration_role = None

        profile = DestinyProfile(ctx=ctx, discord_member=ctx.author, discord_guild=ctx.guild)
        if not (result := await profile.is_registered()):
            # send error message
            await ctx.send(
                embeds=embed_message(
                    "Registration Required",
                    "You are not worthy ... yet\nPlease `/register` with me, then you can use my commands",
                    "Note: Registration is only valid for a year, so you might need to re-register now",
                )
            )

            # check if user has the registration role
            if registration_role and registration_role in ctx.author.roles:
                await ctx.author.remove_role(role=registration_role, reason="Registration outdated")

        else:
            # add registration role
            if registration_role and registration_role not in ctx.author.roles:
                await ctx.author.add_role(role=registration_role, reason="Successful registration")

        return result
