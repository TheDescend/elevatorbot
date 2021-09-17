import asyncio

import discord
import pytz
from dateutil.parser import ParserError, parse
from discord.ext.commands import Cog
from discord_slash import ComponentContext, SlashContext, cog_ext
from discord_slash.utils import manage_components
from discord_slash.utils.manage_commands import create_choice, create_option

from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.commandHelpers.responseTemplates import respond_timeout
from ElevatorBot.core.destiny.lfgSystem import LfgMessage
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.misc.helperFunctions import get_now_with_tz
from ElevatorBot.static.timezones import timezones_dict


class LfgEdit(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_subcommand(
        base="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        name="edit",
        description="When you fucked up and need to edit an event",
        options=[
            create_option(
                name="lfg_id",
                description="The lfg message id",
                option_type=4,
                required=True,
            ),
            create_option(
                name="section",
                description="What section to edit",
                option_type=3,
                required=True,
                choices=[
                    create_choice(name="Activity", value="Activity"),
                    create_choice(name="Description", value="Description"),
                    create_choice(name="Start Time", value="Start Time"),
                    create_choice(name="Maximum Members", value="Maximum Members"),
                ],
            ),
        ],
    )
    async def _edit(self, ctx: SlashContext, lfg_id: int, section: str):
        # get the message obj
        lfg_message = await LfgMessage.from_lfg_id(lfg_id=lfg_id, client=ctx.bot, guild=ctx.guild)

        # error if that is not an lfg message
        if type(lfg_message) is BackendResult:
            await lfg_message.send_error_message(ctx=ctx, hidden=True)
            return

        # might take a sec
        await ctx.defer()

        # make sure the author replies to all further inputs
        def message_check(check_msg: discord.Message):
            return check_msg.author == ctx.author and check_msg.channel == message.channel

        def component_check(check_ctx: ComponentContext):
            return check_ctx.author == ctx.author

        answer_msg = None
        match section:
            case "Activity":
                message = await ctx.send(embed=embed_message("Activity Name", "Please enter a new name"))

                # wait 60s for message
                try:
                    answer_msg = await self.client.wait_for("message", timeout=60.0, check=message_check)
                except asyncio.TimeoutError:
                    await respond_timeout(message=message)
                    return
                else:
                    # edit the message
                    lfg_message.activity = answer_msg.content

            case "Description":
                message = await ctx.send(embed=embed_message("Description", "Please enter a new description"))

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
                    embed=embed_message(
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
                            embed=embed_message(
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
                        manage_components.create_actionrow(
                            manage_components.create_select(
                                options=[
                                    manage_components.create_select_option(
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

                    await message.edit(components=components, embed=embed)

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
                                embed=embed_message(
                                    "Error",
                                    "The event cannot start in the past. Please try again",
                                ),
                            )
                            return

                        lfg_message.start_time = start_time

            # Maximum Members
            case _:
                message = await ctx.send(embed=embed_message("Maximum Members", "Please enter the new maximum members"))

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
                            embed=embed_message(
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

        await message.edit(
            embed=embed_message(f"Success", f"I've edited the post"),
            components=[]
        )


def setup(client):
    client.add_cog(LfgEdit(client))
