from dis_snek.models import InteractionContext, Member, slash_command

from ElevatorBot.commandHelpers.optionTemplates import (
    default_class_option,
    default_stat_option,
    default_user_option,
)
from ElevatorBot.commandHelpers.subCommandTemplates import stat_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.stat import StatScope, get_stat_and_send, stat_translation


class StatPvP(BaseScale):
    @slash_command(
        **stat_sub_command,
        sub_cmd_name="pvp",
        sub_cmd_description="Displays information for all PvP activities",
    )
    @default_stat_option()
    @default_class_option(description="You can restrict the class where the stats count. Default: All classes")
    @default_user_option()
    async def _pvp(self, ctx: InteractionContext, name: str, destiny_class: str = None, user: Member = None):
        user = user or ctx.author
        await get_stat_and_send(
            ctx=ctx,
            member=user,
            destiny_class=destiny_class,
            stat_vanity_name=name,
            stat_bungie_name=stat_translation[name],
            scope=StatScope.PVP,
        )


def setup(client):
    StatPvP(client)
