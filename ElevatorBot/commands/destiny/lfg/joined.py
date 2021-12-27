from dis_snek.models import (
    InteractionContext,
    Timestamp,
    TimestampStyles,
    slash_command,
)

from ElevatorBot.backendNetworking.destiny.lfgSystem import DestinyLfgSystem
from ElevatorBot.commandHelpers.subCommandTemplates import lfg_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message


class LfgJoined(BaseScale):
    @slash_command(
        **lfg_sub_command,
        sub_cmd_name="joined",
        sub_cmd_description="Shows you an overview of all LFG events you have joined",
    )
    async def _joined(self, ctx: InteractionContext):
        # get all the lfg events the user joined
        backend = DestinyLfgSystem(ctx=ctx, discord_guild=ctx.guild)
        result = await backend.user_get_all(discord_member=ctx.author)

        embed = embed_message(f"{ctx.author.display_name}'s LFG Events")

        embed.add_field(
            name="Joined",
            value="\n".join(
                [
                    f"ID `{event.id}` - {event.activity} - {Timestamp.fromdatetime(event.start_time).format(style=TimestampStyles.ShortDateTime)}"
                    for event in result.joined
                ]
            ),
        )
        embed.add_field(
            name="Backup",
            value="\n".join(
                [
                    f"ID `{event.id}` - {event.activity} - {Timestamp.fromdatetime(event.start_time).format(style=TimestampStyles.ShortDateTime)}"
                    for event in result.backup
                ]
            ),
        )

        await ctx.send(embeds=embed, ephemeral=True)


def setup(client):
    LfgJoined(client)
