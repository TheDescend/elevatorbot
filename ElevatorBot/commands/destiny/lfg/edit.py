import asyncio

import pytz
from dateutil.parser import ParserError, parse
from dis_snek.models import (
    ActionRow,
    ComponentContext,
    InteractionContext,
    Message,
    OptionTypes,
    Select,
    SelectOption,
    SlashCommandChoice,
    slash_command,
    slash_option,
)

from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.commandHelpers.responseTemplates import respond_timeout
from ElevatorBot.commandHelpers.subCommandTemplates import lfg_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.lfgSystem import LfgMessage
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.misc.helperFunctions import get_now_with_tz
from ElevatorBot.static.timezones import timezones_dict


class LfgEdit(BaseScale):


    @slash_command(
        **lfg_sub_command,
        sub_cmd_name="edit",
        sub_cmd_description="When you fucked up and need to edit an event",
    )
    @slash_option(name="lfg_id", description="The lfg message id", required=True, opt_type=OptionTypes.INTEGER, min_value=0)
    @slash_option(
        name="section",
        description="What section to edit",
        required=True,
        opt_type=OptionTypes.STRING,
        choices=[
            SlashCommandChoice(name="Activity", value="Activity"),
            SlashCommandChoice(name="Description", value="Description"),
            SlashCommandChoice(name="Start Time", value="Start Time"),
            SlashCommandChoice(name="Maximum Members", value="Maximum Members"),
        ]
    )
    async def _edit(self, ctx: InteractionContext, lfg_id: int, section: str):
        # get the message obj
        lfg_message = await LfgMessage.from_lfg_id(lfg_id=lfg_id, client=ctx.bot, guild=ctx.guild)

        # error if that is not an lfg message
        if type(lfg_message) is BackendResult:
            await lfg_message.send_error_message(ctx=ctx, hidden=True)
            return

        # might take a sec
        await ctx.defer()

        # make sure the author replies to all further inputs
        def message_check(check_msg: Message):
            return check_msg.author == ctx.author and check_msg.channel == message.channel

        def component_check(check_ctx: ComponentContext):
            return check_ctx.author == ctx.author

        answer_msg = None
        match section:
            case "Activity":
                message = await ctx.send(embeds=embed_message("Activity Name", "Please enter a new name"))

                # wait 60s for message
                # todo
                try:
                    answer_msg = await self.client.wait_for("message", timeout=60.0, check=message_check)
                except asyncio.TimeoutError:
                    await respond_timeout(message=message)
                    return
                else:
                    # edit the message
                    lfg_message.activity = answer_msg.content

            case "Description":
                message = await ctx.send(embeds=embed_message("Description", "Please enter a new description"))

                # wait 60s for message
                try:
                    answer_msg = await self.client.wait_for("message", timeout=60.0, check=message_check)
                except asyncio.TimeoutError:
                    await respond_timeout(message=message)
                    return
                else:
                    # edit the message
                    lfg_message.description = answer_msg.content

            case "Start Time":
                message = await ctx.send(
                    embeds=embed_message(
                        "Start Time",
                        "Please enter a new start time like this \n`HH:MM DD/MM`"
                    )
                )

                # wait 60s for message
                try:
                    answer_msg = await self.client.wait_for("message", timeout=60.0, check=message_check)
                except asyncio.TimeoutError:
                    await respond_timeout(message=message)
                    return
                else:
                    # get the datetime
                    try:
                        start_time = parse(answer_msg.content, dayfirst=True)
                    except ParserError:
                        await message.edit(
                            embeds=embed_message(
                                "Error",
                                "There was an error with the formatting of the time parameters, please try again",
                            )
                        )
                        await answer_msg.delete()
                        return
                    await answer_msg.delete()
                    answer_msg = None

                    # ask for the timezone
                    components = [
                        ActionRow(
                            Select(
                                options=[
                                    SelectOption(
                                        emoji="🕑",
                                        label=timezone_name,
                                        value=timezone_value,
                                    )
                                    # Options for timezones
                                    for timezone_name, timezone_value in timezones_dict.items()
                                ],
                                placeholder="Select timezone here",
                                min_values=1,
                                max_values=1,
                            )
                        ),
                    ]
                    embed = embed_message(
                        "Please Select the Timezone",
                    )

                    await message.edit(components=components, embeds=embed)

                    # wait 60s for selection
                    try:
                        select_ctx: ComponentContext = await manage_components.wait_for_component(
                            ctx.bot, components=components, timeout=60, check=component_check
                        )
                    except asyncio.TimeoutError:
                        await respond_timeout(message=message)
                        return
                    else:
                        selected = select_ctx.selected_options[0]

                        # localize to that timezone
                        tz = pytz.timezone(selected)
                        start_time = tz.localize(start_time)

                        # make sure that is in the future
                        if start_time < get_now_with_tz():
                            await select_ctx.edit_origin(
                                components=None,
                                embeds=embed_message(
                                    "Error",
                                    "The event cannot start in the past. Please try again",
                                ),
                            )
                            return

                        old_start_time = lfg_message.start_time
                        lfg_message.start_time = start_time

            # Maximum Members
            case _:
                message = await ctx.send(embeds=embed_message("Maximum Members", "Please enter the new maximum members"))

                # wait 60s for message
                try:
                    answer_msg = await self.client.wait_for("message", timeout=60.0, check=message_check)
                except asyncio.TimeoutError:
                    await respond_timeout(message=message)
                    return
                else:
                    # edit the message
                    try:
                        lfg_message.max_joined_members = int(answer_msg.content)
                    except ValueError:
                        await message.edit(
                            embeds=embed_message(
                                "Error",
                                f"`{answer_msg.content}` is not a number. Please try again",
                            )
                        )
                        await answer_msg.delete()
                        return

        # delete old msgs
        if answer_msg:
            await answer_msg.delete()

        # resend msg
        await lfg_message.send()
        if section == "Start Time":
            await lfg_message.alert_start_time_changed(previous_start_time=old_start_time)

        await message.edit(
            embeds=embed_message(f"Success", f"I've edited the post"),
            components=[]
        )


def setup(client):
    LfgEdit(client)
