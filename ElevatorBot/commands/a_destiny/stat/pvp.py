from naff import Member, slash_command

from ElevatorBot.commandHelpers.optionTemplates import default_class_option, default_stat_option, default_user_option
from ElevatorBot.commandHelpers.subCommandTemplates import stat_sub_command
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.destiny.stat import get_stat_and_send, stat_translation
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.static.destinyEnums import StatScope


class StatPvP(BaseModule):
    @slash_command(
        **stat_sub_command,
        sub_cmd_name="pvp",
        sub_cmd_description="Displays the specified stat for all PvP activities",
        dm_permission=False,
    )
    @default_stat_option(pvp=True)
    @default_class_option()
    @default_user_option()
    async def pvp(self, ctx: ElevatorInteractionContext, name: str, destiny_class: str = None, user: Member = None):
        member = user or ctx.author
        await get_stat_and_send(
            ctx=ctx,
            member=member,
            destiny_class=destiny_class,
            stat_vanity_name=name,
            stat_bungie_name=stat_translation[name],
            scope=StatScope.PvP,
        )


def setup(client):
    StatPvP(client)
