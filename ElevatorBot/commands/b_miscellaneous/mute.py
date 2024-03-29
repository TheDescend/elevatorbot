import asyncio
import datetime

from naff import Member, OptionTypes, SlashCommandChoice, Timestamp, TimestampStyles, slash_command, slash_option

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commandHelpers.permissionTemplates import restrict_default_permission
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.discordShortcutFunctions import assign_roles_to_member, remove_roles_from_member
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.misc.moderation import Moderation
from Shared.functions.helperFunctions import get_now_with_tz
from Shared.functions.readSettingsFile import get_setting

# =============
# Descend Only!
# =============


muted_ids = {0: "Muted", get_setting("DESCEND_ROLE_NO_NICKNAME_ID"): "Muted - No Nickname"}


class Mute(BaseModule):
    @slash_command(
        name="mute",
        description="Mutes the specified user",
        dm_permission=False,
        scopes=get_setting("COMMAND_GUILD_SCOPE"),
    )
    @default_user_option(description="Which user to mute", required=True)
    @slash_option(
        name="muted_type",
        description="How should the user be muted",
        required=True,
        opt_type=OptionTypes.STRING,
        choices=[SlashCommandChoice(name=name, value=str(role_id)) for role_id, name in muted_ids.items()],
    )
    @slash_option(
        name="hours",
        description="How many hours to mute the user for",
        required=True,
        opt_type=OptionTypes.INTEGER,
        min_value=1,
    )
    @slash_option(
        name="reason",
        description="Whats the reason for the mute",
        required=True,
        opt_type=OptionTypes.STRING,
    )
    @restrict_default_permission()
    async def mute(self, ctx: ElevatorInteractionContext, user: Member, muted_type: str, hours: int, reason: str):
        muted_type = int(muted_type)
        unmute_date = get_now_with_tz() + datetime.timedelta(hours=hours)

        # add it to the backend logs
        backend = Moderation(discord_member=user, discord_guild=ctx.guild, ctx=ctx)
        result = await backend.add_mute(
            reason=reason, duration_in_seconds=hours * 60 * 60, mod_discord_id=ctx.author.id
        )
        if not result:
            return

        if muted_type == get_setting("DESCEND_ROLE_NO_NICKNAME_ID"):
            # noinspection PyTypeChecker
            await user.edit_nickname(None)
            await assign_roles_to_member(user, muted_type, reason=f"/mute by {ctx.author}")

        else:
            # time them out instead
            await user.timeout(communication_disabled_until=unmute_date, reason=f"/mute by {ctx.author}")

        unmute_date_formatted = Timestamp.fromdatetime(unmute_date).format(style=TimestampStyles.RelativeTime)
        status = await ctx.send(
            embeds=embed_message(
                "Success",
                f"Muted {user.mention} for {hours} hours. They will be un-muted {unmute_date_formatted}\nI will edit this message once the time is over\n⁣\n**Reason:** `{reason}`",
                f"Type: {muted_ids[muted_type]} | Muted by {ctx.author.username}#{ctx.author.discriminator}",
            )
        )

        await user.send(
            embeds=embed_message(
                f"You have been: {muted_ids[muted_type]}",
                f"You will regain that permission {unmute_date_formatted}\n⁣\n**Reason:** `{reason}`",
                f"Muted by {ctx.author.username}#{ctx.author.discriminator}",
            )
        )

        await asyncio.sleep(hours * 60 * 60)
        await remove_roles_from_member(user, muted_type, reason=f"/mute by {ctx.author}")

        await status.edit(embeds=embed_message("Success", f"{user.mention} is no longer muted"))


def setup(client):
    Mute(client)
