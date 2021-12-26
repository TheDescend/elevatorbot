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

from ElevatorBot.backendNetworking.misc.moderation import Moderation
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.discordShortcutFunctions import (
    assign_roles_to_member,
    remove_roles_from_member,
)
from ElevatorBot.misc.formating import embed_message
from settings import COMMAND_GUILD_SCOPE


class Warning(BaseScale):

    # todo perm
    @slash_command(name="warning", description="Warns the specified user", scopes=COMMAND_GUILD_SCOPE)
    @default_user_option(description="Which user to warn", required=True)
    @slash_option(
        name="reason",
        description="Whats the reason for the warning",
        required=True,
        opt_type=OptionTypes.STRING,
    )
    async def _warning(self, ctx: InteractionContext, user: Member, reason: str):
        backend = Moderation(discord_member=user, discord_guild=ctx.guild, ctx=ctx)
        # get past warnings
        past_warnings = await backend.get_warnings()
        if not past_warnings:
            return

        # add warning to the backend logs
        result = await backend.add_warning(reason=reason, mod_discord_id=ctx.author.id)
        if not result:
            return

        embed = embed_message(
            "Warning",
            f"User has been warned {user.mention}",
            f"Warned by {ctx.author.username}#{ctx.author.discriminator}",
        )
        embed.add_field(name="Reason", value=f"`{reason}`", inline=False)
        if past_warnings.entries:
            embed.add_field(
                name="Past Warnings",
                value="\n".join(
                    [
                        f"Warning on {Timestamp.fromdatetime(entry.date).format(style=TimestampStyles.ShortDateTime)}"
                        for entry in past_warnings.entries
                    ]
                ),
                inline=False,
            )

        await ctx.send(embeds=embed)


def setup(client):
    Warning(client)
