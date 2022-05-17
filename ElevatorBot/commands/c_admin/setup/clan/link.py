from naff import slash_command

from ElevatorBot.commandHelpers.permissionTemplates import restrict_default_permission
from ElevatorBot.commandHelpers.subCommandTemplates import setup_sub_command, setup_sub_command_clan_group
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.base import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.destiny.clan import DestinyClan


class ClanLink(BaseModule):
    """
    Links your own Destiny 2 clan with the discord server this was executed in
    """

    @slash_command(
        **setup_sub_command,
        **setup_sub_command_clan_group,
        sub_cmd_name="link",
        sub_cmd_description="Links your own Destiny 2 clan with this discord",
    )
    @restrict_default_permission()
    async def link(self, ctx: ElevatorInteractionContext):
        clan = DestinyClan(ctx=ctx, discord_guild=ctx.guild)
        result = await clan.link(linked_by=ctx.author)

        await ctx.send(
            embeds=embed_message(
                "Success",
                f"This discord server has been successfully linked to the clan `{result.clan_name}`",
            )
        )


def setup(client):
    ClanLink(client)
