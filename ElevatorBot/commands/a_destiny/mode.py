from dis_snek import InteractionContext, Member, slash_command

from ElevatorBot.commandHelpers.optionTemplates import (
    default_class_option,
    default_expansion_option,
    default_mode_option,
    default_season_option,
    default_time_option,
    default_user_option,
)
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.activity import format_and_send_activity_data
from ElevatorBot.misc.helperFunctions import parse_datetime_options
from ElevatorBot.networking.destiny.activities import DestinyActivities
from Shared.enums.destiny import UsableDestinyActivityModeTypeEnum
from Shared.networkingSchemas.destiny import DestinyActivityInputModel


class DestinyMode(BaseScale):
    @slash_command(name="mode", description="Display stats for Destiny 2 activity modes")
    @default_mode_option(description="Chose the mode you want to see the stats for", required=True)
    @default_class_option()
    @default_expansion_option()
    @default_season_option()
    @default_time_option(
        name="start_time",
        description="Format: `DD/MM/YY` - Input the **earliest** date you want the weapon stats for. Default: Big Bang",
    )
    @default_time_option(
        name="end_time",
        description="Format: `DD/MM/YY` - Input the **latest** date you want the weapon stats for. Default: Now",
    )
    @default_user_option()
    async def mode(
        self,
        ctx: InteractionContext,
        mode: str,
        destiny_class: str = None,
        expansion: str = None,
        season: str = None,
        start_time: str = None,
        end_time: str = None,
        user: Member = None,
    ):
        # parse start and end time
        start_time, end_time = await parse_datetime_options(
            ctx=ctx, expansion=expansion, season=season, start_time=start_time, end_time=end_time
        )
        if not start_time:
            return

        mode = UsableDestinyActivityModeTypeEnum(int(mode))

        member = user or ctx.author
        backend_activities = DestinyActivities(ctx=ctx, discord_member=member, discord_guild=ctx.guild)

        # get the stats
        stats = await backend_activities.get_activity_stats(
            input_model=DestinyActivityInputModel(
                mode=mode.value,
                character_class=destiny_class,
                start_time=start_time,
                end_time=end_time,
            )
        )

        await format_and_send_activity_data(
            ctx=ctx,
            member=member,
            stats=stats,
            name="Activity Mode Stats",
            activity_name=mode.name.capitalize(),
            start_time=start_time,
            end_time=end_time,
            destiny_class=destiny_class,
        )


def setup(client):
    DestinyMode(client)
