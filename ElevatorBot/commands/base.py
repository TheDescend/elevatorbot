from dis_snek.models import InteractionContext, Scale

from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile
from ElevatorBot.commandHelpers.responseTemplates import respond_pending

from ElevatorBot.misc.cache import registered_role_cache
from ElevatorBot.misc.formating import embed_message
from NetworkingSchemas.destiny.profile import DestinyHasTokenModel


class BaseScale(Scale):
    """Add checks to every scale"""

    def __init__(self, client):
        self.client = client
        self.add_scale_check(self.registered_check)
        self.add_scale_check(self.no_dm_check)

    @staticmethod
    async def no_dm_check(ctx: InteractionContext) -> bool:
        """
        Default command that is run before the command is handled
        Checks that the command is not invoked in dms
        """

        if not ctx.guild:
            await ctx.send(
                embeds=embed_message(
                    "Error",
                    "My commands can only be used in a guild and not in DMs",
                ),
            )
            return False
        return True

    @staticmethod
    async def no_pending_check(ctx: InteractionContext) -> bool:
        """
        Default command that is run before the command is handled
        Checks that the command is not invoked by pending members
        """

        if ctx.author.pending:
            await respond_pending(ctx)
            return False
        return True

    @staticmethod
    async def registered_check(ctx: InteractionContext) -> bool:
        """
        Default command that is run before the command is handled
        Checks if the command invoker is registered
        """

        # get the registration role
        registration_role = await registered_role_cache.get(guild=ctx.guild)

        # check in cache if the user is registered
        if await registered_role_cache.is_not_registered(ctx.author.id):
            result = DestinyHasTokenModel(token=False)
        else:
            # todo test
            # check their status with the backend
            result = await DestinyProfile(
                ctx=None, 
                #client=ctx.bot, 
                discord_member=ctx.author, 
                discord_guild=ctx.guild
            ).has_token()

        if not result:
            return False

        if not result.token:
            registered_role_cache.not_registered_users.append(ctx.author.id)

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

        return result.token
