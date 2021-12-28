import asyncio

from dis_snek.models import (
    ActionRow,
    Button,
    ButtonStyles,
    ComponentContext,
    InteractionContext,
    Message,
    OptionTypes,
    slash_command,
    slash_option,
)

from ElevatorBot.commandHelpers.autocomplete import activities
from ElevatorBot.commandHelpers.optionTemplates import (
    autocomplete_activity_option,
    default_time_option,
    get_timezone_choices,
)
from ElevatorBot.commandHelpers.responseTemplates import respond_timeout
from ElevatorBot.commandHelpers.subCommandTemplates import lfg_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.lfg.lfgSystem import LfgMessage
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.misc.helperFunctions import parse_string_datetime
from ElevatorBot.static.destinyActivities import dungeons, raids
from NetworkingSchemas.destiny.activities import DestinyActivityModel


# todo switch start time / timezone / description / max member overwrite to modals (show current max members)
class LfgCreate(BaseScale):
    @slash_command(
        **lfg_sub_command,
        sub_cmd_name="create",
        sub_cmd_description="Creates an LFG event",
    )
    @autocomplete_activity_option(description="The name of the activity", required=True)
    @default_time_option(
        name="start_time",
        description="Format: `HH:MM DD/MM` - When the event is supposed to start. `asap` to start as soon as it fills up",
        required=True,
    )
    @slash_option(
        name="timezone",
        description="What timezone you are in",
        required=True,
        opt_type=OptionTypes.STRING,
        choices=get_timezone_choices(),
    )
    @slash_option(
        name="overwrite_max_members",
        description="You can overwrite the maximum number of people that can join your event",
        required=False,
        opt_type=OptionTypes.INTEGER,
        min_value=1,
        max_value=50,
    )
    async def _create(
        self, ctx: InteractionContext, activity: str, start_time: str, timezone: str, overwrite_max_members: int = None
    ):
        # get the actual activity
        activity = activities[activity]

        if start_time.lower() != "asap":
            start_time = await parse_string_datetime(ctx=ctx, time=start_time, timezone=timezone)
            if not start_time:
                return

        max_joined_members = activity.max_players

        # todo modal
        description = "placeholder until modals come out"
        if overwrite_max_members:
            max_joined_members = overwrite_max_members

        # create lfg message
        lfg_message = await LfgMessage.create(
            ctx=ctx,
            activity=activity.name,
            description=description,
            start_time=start_time,
            max_joined_members=max_joined_members,
        )

        await ctx.send(
            embeds=embed_message(
                f"Success", f"I have created the post, click [here]({lfg_message.message.jump_url}) to view it"
            )
        )


def setup(client):
    LfgCreate(client)
