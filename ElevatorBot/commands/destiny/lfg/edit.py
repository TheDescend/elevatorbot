import asyncio

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

from ElevatorBot.commandHelpers.optionTemplates import (
    autocomplete_activity_option,
    lfg_event_id,
)
from ElevatorBot.commandHelpers.responseTemplates import respond_timeout
from ElevatorBot.commandHelpers.subCommandTemplates import lfg_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.lfg.lfgSystem import LfgMessage
from ElevatorBot.misc.discordShortcutFunctions import has_admin_permission
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.misc.helperFunctions import parse_string_datetime
from ElevatorBot.static.timezones import timezones_dict


# todo switch start time / timezone / description / max member overwrite to modals (show current max members)
class LfgEdit(BaseScale):
    @slash_command(
        **lfg_sub_command,
        sub_cmd_name="edit",
        sub_cmd_description="When you fucked up and need to edit an event",
    )
    @lfg_event_id()
    @autocomplete_activity_option(description="Use this is you want to edit the name of the activity", required=False)
    async def _edit(self, ctx: InteractionContext, lfg_id: int, activity: str):
        await ctx.send("Requires modal")
        return

        # get the message obj
        lfg_message = await LfgMessage.from_lfg_id(ctx=ctx, lfg_id=lfg_id, client=ctx.bot, guild=ctx.guild)

        # error if that is not an lfg message
        if not lfg_message:
            return

        # test if the user is admin or author
        if ctx.author.id != lfg_message.author_id:
            if not await has_admin_permission(ctx=ctx, member=ctx.author):
                return

        # get the actual activity
        activity = activities[activity]

        # todo modal
        ...

        # # resend msg
        # await lfg_message.send()
        # if section == "Start Time":
        #     await lfg_message.alert_start_time_changed(previous_start_time=old_start_time)

        await ctx.send(
            embeds=embed_message(
                f"Success", f"I have edited the post, click [here]({lfg_message.message.jump_url}) to view it"
            ),
            components=[],
        )


def setup(client):
    LfgEdit(client)
