import asyncio

from dis_snek import InteractionContext, Modal, OptionTypes, ParagraphText, slash_command, slash_option

from ElevatorBot.commandHelpers import autocomplete
from ElevatorBot.commandHelpers.optionTemplates import (
    autocomplete_activity_option,
    default_time_option,
    get_timezone_choices,
)
from ElevatorBot.commandHelpers.responseTemplates import respond_timeout
from ElevatorBot.commandHelpers.subCommandTemplates import lfg_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.lfg.lfgSystem import LfgMessage
from ElevatorBot.misc.helperFunctions import parse_string_datetime


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
    async def create(
        self, ctx: InteractionContext, activity: str, start_time: str, timezone: str, overwrite_max_members: int = None
    ):
        # get the actual activity
        activity = autocomplete.activities[activity]

        if start_time.lower() != "asap":
            start_time = await parse_string_datetime(
                ctx=ctx, time=start_time, timezone=timezone, can_start_in_past=False
            )
            if not start_time:
                return

        max_joined_members = activity.max_players

        # get the description
        if overwrite_max_members:
            max_joined_members = overwrite_max_members

        # ask more info in a modal
        modal = Modal(
            title="LFG Information",
            components=[
                ParagraphText(
                    label="Updated Description for the LFG Event",
                    custom_id="description",
                    placeholder="Required",
                    min_length=5,
                    max_length=500,
                    required=True,
                ),
            ],
        )
        await ctx.send_modal(modal=modal)

        # wait 5 minutes for them to fill it out
        try:
            modal_ctx = await ctx.bot.wait_for_modal(modal=modal, timeout=300)

        except asyncio.TimeoutError:
            # give timeout message
            await respond_timeout(ctx=ctx)
            return

        # create lfg message
        await LfgMessage.create(
            ctx=modal_ctx,
            activity=activity.name,
            description=modal_ctx.responses["description"],
            start_time=start_time,
            max_joined_members=max_joined_members,
        )


def setup(client):
    command = LfgCreate(client)

    # register the autocomplete callback
    command.create.autocomplete("activity")(autocomplete.autocomplete_send_activity_name)
