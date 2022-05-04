import asyncio

from dis_snek import InteractionContext, Modal, OptionTypes, ParagraphText, slash_command, slash_option

from ElevatorBot.commandHelpers import autocomplete
from ElevatorBot.commandHelpers.optionTemplates import (
    autocomplete_activity_option,
    default_time_option,
    get_timezone_choices,
    lfg_event_id,
)
from ElevatorBot.commandHelpers.responseTemplates import respond_timeout
from ElevatorBot.commandHelpers.subCommandTemplates import lfg_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.lfg.lfgSystem import LfgMessage
from ElevatorBot.misc.discordShortcutFunctions import has_admin_permission
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.misc.helperFunctions import parse_string_datetime


class LfgEdit(BaseScale):
    @slash_command(
        **lfg_sub_command,
        sub_cmd_name="edit",
        sub_cmd_description="When you fucked up and need to edit an event",
    )
    @lfg_event_id()
    @autocomplete_activity_option(
        description="Use this is you want to edit the name of the activity",
        required=False,
    )
    @default_time_option(
        name="start_time",
        description="Format: `HH:MM DD/MM` - Use this is you want to edit the start time of the activity",
        required=False,
    )
    @slash_option(
        name="timezone",
        description="Use this is you want to edit the start time of the activity",
        required=False,
        opt_type=OptionTypes.STRING,
        choices=get_timezone_choices(),
    )
    @slash_option(
        name="overwrite_max_members",
        description="Use this is you want to edit the maximum number participants of the activity",
        required=False,
        opt_type=OptionTypes.INTEGER,
        min_value=1,
        max_value=50,
    )
    async def edit(
        self,
        ctx: InteractionContext,
        lfg_id: int,
        activity: str = None,
        start_time: str = None,
        timezone: str = None,
        overwrite_max_members: int = None,
    ):
        if start_time:
            if not timezone:
                await ctx.send(
                    embed=embed_message(
                        "Error",
                        "If you want to change the `start time`, you need to specify the `timezone` as well",
                    ),
                    ephemeral=True,
                )
                return

        if start_time:
            if start_time.lower() != "asap":
                start_time = await parse_string_datetime(
                    ctx=ctx, time=start_time, timezone=timezone, can_start_in_past=False
                )
                if not start_time:
                    return

        # get the actual activity
        if activity:
            activity = autocomplete.activities[activity.lower()]

        # get the message obj
        lfg_message = await LfgMessage.from_lfg_id(ctx=ctx, lfg_id=lfg_id, client=ctx.bot, guild=ctx.guild)

        # error if that is not an lfg message
        if not lfg_message:
            return

        # test if the user is admin or author
        if ctx.author.id != lfg_message.author_id:
            if not await has_admin_permission(ctx=ctx, member=ctx.author):
                return

        # ask the other info in a modal
        modal = Modal(
            title="LFG Information",
            components=[
                ParagraphText(
                    label="Description for the LFG Event",
                    custom_id="description",
                    value=lfg_message.description,
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

        # update the data
        sort = False
        if start_time:
            await lfg_message.alert_start_time_changed(new_start_time=start_time)
            sort = True
        if overwrite_max_members:
            lfg_message.max_joined_members = overwrite_max_members
        if activity:
            lfg_message.activity = activity.name
        if (description := modal_ctx.responses["description"]) != lfg_message.description:
            lfg_message.description = description

        # resend msg
        await lfg_message.send(force_sort=sort)

        await modal_ctx.send(
            embeds=embed_message(
                "Success", f"I have edited the post, click [here]({lfg_message.message.jump_url}) to view it"
            )
        )


def setup(client):
    command = LfgEdit(client)

    # register the autocomplete callback
    command.edit.autocomplete("activity")(autocomplete.autocomplete_send_activity_name)
