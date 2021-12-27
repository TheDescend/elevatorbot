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

from ElevatorBot.commandHelpers.optionTemplates import (
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


# todo wait for modal
class LfgCreate(BaseScale):
    @slash_command(
        **lfg_sub_command,
        sub_cmd_name="create",
        sub_cmd_description="Creates an LFG event",
    )
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
    async def _create(self, ctx: InteractionContext, start_time: str, timezone: str, overwrite_max_members: int = None):
        await ctx.send("This needs modals")
        return

        # if start_time.lower() != "asap":
        #     start_time = await parse_string_datetime(ctx=ctx, time=start_time, timezone=timezone)
        #     if not start_time:
        #         return
        #
        # # ask for the activity
        # components = [
        #     ActionRow(
        #         Button(style=ButtonStyles.GREEN, label="Raids"),
        #         Button(style=ButtonStyles.GREEN, label="Dungeons"),
        #         Button(style=ButtonStyles.GREEN, label="Trials"),
        #         Button(style=ButtonStyles.GREEN, label="Iron Banner"),
        #         Button(style=ButtonStyles.GREEN, label="Other"),
        #     ),
        # ]
        # embed = embed_message(
        #     "Please Select the Activity",
        # )
        #
        # message = await ctx.send(components=components, embeds=embed)
        #
        # # wait 60s for button press
        # # todo
        # try:
        #     button_ctx: ComponentContext = await manage_components.wait_for_component(
        #         ctx.bot, components=components, timeout=60
        #     )
        # except asyncio.TimeoutError:
        #     await respond_timeout(message=message)
        #     return
        # else:
        #     # make sure the author replies to all further inputs
        #     def message_check(check_msg: Message):
        #         return check_msg.author == ctx.author and check_msg.channel == message.channel
        #
        #     def component_check(check_ctx: ComponentContext):
        #         return check_ctx.author == ctx.author
        #
        #     # handle all button presses separately:
        #     match button_ctx.component["label"]:
        #         # Raids
        #         case "Raids":
        #             components = manage_components.spread_to_rows(
        #                 *[manage_components.create_button(style=ButtonStyle.blue, label=raid) for raid in raids]
        #             )
        #             embed = embed_message(
        #                 "Please Select the Raid",
        #             )
        #
        #             await button_ctx.edit_origin(components=components, embeds=embed)
        #
        #             # wait 60s for button press
        #             try:
        #                 button_ctx: ComponentContext = await manage_components.wait_for_component(
        #                     ctx.bot, components=components, timeout=60, check=component_check
        #                 )
        #             except asyncio.TimeoutError:
        #                 await respond_timeout(message=message)
        #                 return
        #             else:
        #                 await button_ctx.edit_origin(embeds=embed)
        #                 activity = button_ctx.component["label"]
        #                 max_joined_members = 6
        #
        #         # Dungeons
        #         case "Dungeons":
        #             components = [
        #                 *[
        #                     manage_components.create_button(style=ButtonStyle.blue, label=dungeon)
        #                     for dungeon in dungeons
        #                 ]
        #             ]
        #             embed = embed_message(
        #                 "Please Select the Dungeon",
        #             )
        #
        #             await button_ctx.edit_origin(components=components, embeds=embed)
        #
        #             # wait 60s for button press
        #             try:
        #                 button_ctx: ComponentContext = await manage_components.wait_for_component(
        #                     ctx.bot, components=components, timeout=60, check=component_check
        #                 )
        #             except asyncio.TimeoutError:
        #                 await respond_timeout(message=message)
        #                 return
        #             else:
        #                 await button_ctx.edit_origin(embeds=embed)
        #                 activity = button_ctx.component["label"]
        #                 max_joined_members = 3
        #
        #         # Trials
        #         case "Trials":
        #             activity = button_ctx.component["label"]
        #             max_joined_members = 3
        #
        #         # Iron Banner
        #         case "Iron Banner":
        #             activity = button_ctx.component["label"]
        #             max_joined_members = 6
        #
        #         # Other
        #         case _:
        #             await button_ctx.edit_origin(
        #                 components=None,
        #                 embeds=embed_message("Activity Name", "Please enter a name"),
        #             )
        #
        #             # wait 60s for message
        #             try:
        #                 answer_msg = await self.client.wait_for("message", timeout=60.0, check=message_check)
        #             except asyncio.TimeoutError:
        #                 await respond_timeout(message=message)
        #                 return
        #             else:
        #                 activity = answer_msg.content
        #                 max_joined_members = 12
        #
        #                 await answer_msg.delete()
        #
        #     # do the max_joined_members overwrite if asked for
        #     if overwrite_max_members:
        #         max_joined_members = overwrite_max_members
        #
        #     # get the description
        #     await message.edit(
        #         components=None,
        #         embeds=embed_message("Description", "Please enter a description"),
        #     )
        #
        #     try:
        #         answer_msg = await self.client.wait_for("message", timeout=60.0, check=message_check)
        #     except asyncio.TimeoutError:
        #         await respond_timeout(message=message)
        #         return
        #     else:
        #         description = answer_msg.content
        #         await answer_msg.delete()
        #
        #     # create lfg message
        #     await LfgMessage.create(
        #         ctx=ctx,
        #         activity=activity,
        #         description=description,
        #         start_time=start_time,
        #         max_joined_members=max_joined_members,
        #     )
        #
        #     await message.edit(embeds=embed_message(f"Success", f"I've created the post"))


def setup(client):
    LfgCreate(client)
