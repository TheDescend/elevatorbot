import asyncio
import datetime

from dis_snek.models import (
    InteractionContext,
    Member,
    OptionTypes,
    SlashCommandChoice,
    Timestamp,
    TimestampStyles,
    slash_command,
    slash_option,
)

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.discordShortcutFunctions import (
    assign_roles_to_member,
    remove_roles_from_member,
)
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.misc.helperFunctions import get_now_with_tz
from ElevatorBot.static.descendOnlyIds import (
    descend_muted_ids,
    descend_no_nickname_role_id,
)
from settings import COMMAND_GUILD_SCOPE


class Mute(BaseScale):

    # todo perm
    @slash_command(name="mute", description="Mutes the specified user", scopes=COMMAND_GUILD_SCOPE)
    @default_user_option(description="Which user to mute", required=True)
    @slash_option(
        name="muted_type",
        description="How should the user be muted",
        required=True,
        opt_type=OptionTypes.STRING,
        choices=[SlashCommandChoice(name=name, value=str(role_id)) for role_id, name in descend_muted_ids.items()],
    )
    @slash_option(
        name="hours",
        description="How many hours to mute the user for",
        required=True,
        opt_type=OptionTypes.INTEGER,
        min_value=1,
    )
    async def _mute(self, ctx: InteractionContext, user: Member, muted_type: str, hours: int):
        muted_type = int(muted_type)

        if muted_type == descend_no_nickname_role_id:
            # todo test if that removes it
            await user.edit_nickname("")

        await assign_roles_to_member(user, muted_type, reason=f"/mute by {ctx.author}")

        unmute_date = get_now_with_tz() + datetime.timedelta(hours=hours)
        unmute_date_formatted = Timestamp.fromdatetime(unmute_date).format(style=TimestampStyles.RelativeTime)
        status = await ctx.send(
            embeds=embed_message(
                "Success",
                f"Muted {user.mention} for {hours} hours. They will be un-muted {unmute_date_formatted}\nI will edit this message once the time is over",
                f"Type: {descend_muted_ids[muted_type]}",
            )
        )

        await user.send(
            embeds=embed_message(
                f"You have been: {descend_muted_ids[muted_type]}",
                f"You will regain that permission {unmute_date_formatted}",
            )
        )

        await asyncio.sleep(hours * 60 * 60)
        await remove_roles_from_member(user, muted_type, reason=f"/mute by {ctx.author}")

        await status.edit(embeds=embed_message("Success", f"{user.mention} is no longer muted"))


def setup(client):
    Mute(client)
