from naff import slash_command

from ElevatorBot.commandHelpers.permissionTemplates import restrict_default_permission
from ElevatorBot.commandHelpers.subCommandTemplates import setup_sub_command, setup_sub_command_clan_group
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.destiny.clan import DestinyClan


class ClanUnlink(BaseModule):
    """
    Unlinks the current Destiny 2 clan and the discord server this was executed in
    """

    @slash_command(
        **setup_sub_command,
        **setup_sub_command_clan_group,
        sub_cmd_name="unlink",
        sub_cmd_description="Unlink the current Destiny 2 clan with this server",
        dm_permission=False,
    )
    @restrict_default_permission()
    async def unlink(self, ctx: ElevatorInteractionContext):
        clan = DestinyClan(ctx=ctx, discord_guild=ctx.guild)
        result = await clan.unlink(unlinked_by=ctx.author)

        await ctx.send(
            embeds=embed_message(
                "Success",
                f"This discord server has been successfully unlinked from the clan `{result.clan_name}`",
            )
        )


def setup(client):
    ClanUnlink(client)
