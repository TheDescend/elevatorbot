import asyncio


import pytz
from dateutil.parser import parse, ParserError
from dis_snek.models import ActionRow, Button, ButtonStyles, ComponentContext, InteractionContext, Message, OptionTypes, slash_option, sub_command

from ElevatorBot.commandHelpers.optionTemplates import destiny_group, get_timezone_choices
from ElevatorBot.commandHelpers.responseTemplates import (
    respond_invalid_time_input,
    respond_time_input_in_past,
    respond_timeout,
)
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.lfgSystem import LfgMessage
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.misc.helperFunctions import get_now_with_tz
from ElevatorBot.static.destinyActivities import dungeons, raids
from ElevatorBot.static.timezones import timezones_dict


class LfgCreate(BaseScale):


    @sub_command(
        base_name="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        sub_name="create",
        sub_description="Creates an LFG post",
        **destiny_group,
    )
    @slash_option(name="start_time", description="Format: 'HH:MM DD/MM' - When the event is supposed to start", required=True, opt_type=OptionTypes.STRING)
    @slash_option(name="timezone", description="What timezone you are in", required=True, opt_type=OptionTypes.STRING, choices=get_timezone_choices())
    @slash_option(name="overwrite_max_members", description="You can overwrite the maximum number of people that can join your event", required=False, opt_type=OptionTypes.INTEGER)
    async def _create(self, ctx: InteractionContext, start_time: str, timezone: str, overwrite_max_members: int = None):
        # get start time
        try:
            start_time = parse(start_time, dayfirst=True)
        except ParserError:
            await respond_invalid_time_input(ctx=ctx)
            return

        # make that timezone aware
        tz = pytz.timezone(timezone)
        start_time = tz.localize(start_time)

        # make sure that is in the future
        if start_time < get_now_with_tz():
            await respond_time_input_in_past(ctx=ctx)
            return

        # might take a sec
        await ctx.defer()

        # ask for the activity
        components = [
            ActionRow(
                Button(style=ButtonStyles.BLUE, label="Raids"),
                Button(style=ButtonStyles.BLUE, label="Dungeons"),
                Button(style=ButtonStyles.BLUE, label="Trials"),
                Button(style=ButtonStyles.BLUE, label="Iron Banner"),
                Button(style=ButtonStyles.BLUE, label="Other"),
            ),
        ]
        embed = embed_message(
            "Please Select the Activity",
        )

        message = await ctx.send(components=components, embeds=embed)

        # wait 60s for button press
        # todo
        try:
            button_ctx: ComponentContext = await manage_components.wait_for_component(
                ctx.bot, components=components, timeout=60
            )
        except asyncio.TimeoutError:
            await respond_timeout(message=message)
            return
        else:
            # make sure the author replies to all further inputs
            def message_check(check_msg: Message):
                return check_msg.author == ctx.author and check_msg.channel == message.channel

            def component_check(check_ctx: ComponentContext):
                return check_ctx.author == ctx.author

            # handle all button presses separately:
            match button_ctx.component["label"]:
                # Raids
                case "Raids":
                    components = manage_components.spread_to_rows(
                        *[
                            manage_components.create_button(style=ButtonStyle.blue, label=raid)
                            for raid in raids
                        ]
                    )
                    embed = embed_message(
                        "Please Select the Raid",
                    )

                    await button_ctx.edit_origin(components=components, embeds=embed)

                    # wait 60s for button press
                    try:
                        button_ctx: ComponentContext = await manage_components.wait_for_component(
                            ctx.bot, components=components, timeout=60, check=component_check
                        )
                    except asyncio.TimeoutError:
                        await respond_timeout(message=message)
                        return
                    else:
                        await button_ctx.edit_origin(embeds=embed)
                        activity = button_ctx.component["label"]
                        max_joined_members = 6

                # Dungeons
                case "Dungeons":
                    components = [
                        *[
                            manage_components.create_button(style=ButtonStyle.blue, label=dungeon)
                            for dungeon in dungeons
                        ]
                    ]
                    embed = embed_message(
                        "Please Select the Dungeon",
                    )

                    await button_ctx.edit_origin(components=components, embeds=embed)

                    # wait 60s for button press
                    try:
                        button_ctx: ComponentContext = await manage_components.wait_for_component(
                            ctx.bot, components=components, timeout=60, check=component_check
                        )
                    except asyncio.TimeoutError:
                        await respond_timeout(message=message)
                        return
                    else:
                        await button_ctx.edit_origin(embeds=embed)
                        activity = button_ctx.component["label"]
                        max_joined_members = 3

                # Trials
                case "Trials":
                    activity = button_ctx.component["label"]
                    max_joined_members = 3

                # Iron Banner
                case "Iron Banner":
                    activity = button_ctx.component["label"]
                    max_joined_members = 6

                # Other
                case _:
                    await button_ctx.edit_origin(
                        components=None,
                        embeds=embed_message("Activity Name", "Please enter a name"),
                    )

                    # wait 60s for message
                    try:
                        answer_msg = await self.client.wait_for("message", timeout=60.0, check=message_check)
                    except asyncio.TimeoutError:
                        await respond_timeout(message=message)
                        return
                    else:
                        activity = answer_msg.content
                        max_joined_members = 12

                        await answer_msg.delete()

            # do the max_joined_members overwrite if asked for
            if overwrite_max_members:
                max_joined_members = overwrite_max_members

            # get the description
            await message.edit(
                components=None,
                embeds=embed_message("Description", "Please enter a description"),
            )

            try:
                answer_msg = await self.client.wait_for("message", timeout=60.0, check=message_check)
            except asyncio.TimeoutError:
                await respond_timeout(message=message)
                return
            else:
                description = answer_msg.content
                await answer_msg.delete()

            # create lfg message
            await LfgMessage.create(
                ctx=ctx,
                activity=activity,
                description=description,
                start_time=start_time,
                max_joined_members=max_joined_members,
            )

            await message.edit(embeds=embed_message(f"Success", f"I've created the post"))


def setup(client):
    LfgCreate(client)
