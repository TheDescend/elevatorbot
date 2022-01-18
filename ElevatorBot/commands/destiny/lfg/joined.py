from dis_snek.models import InteractionContext, Timestamp, TimestampStyles, slash_command

from ElevatorBot.backendNetworking.destiny.lfgSystem import DestinyLfgSystem
from ElevatorBot.commandHelpers.subCommandTemplates import lfg_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formatting import embed_message
from Shared.networkingSchemas import LfgOutputModel


class LfgJoined(BaseScale):
    @slash_command(
        **lfg_sub_command,
        sub_cmd_name="joined",
        sub_cmd_description="Shows you an overview of all LFG events you have joined",
    )
    async def joined(self, ctx: InteractionContext):
        # get all the lfg events the user joined
        backend = DestinyLfgSystem(ctx=ctx, discord_guild=ctx.guild)
        result = await backend.user_get_all(discord_member=ctx.author)

        embed = embed_message(
            "LFG Events",
            None if result.joined or result.backup else "You have not currently joined any LFG events",
            member=ctx.author,
        )

        if result.joined:
            embed.add_field(
                name="Joined",
                value="\n".join([self._format_event(event) for event in result.joined]),
            )
        if result.backup:
            embed.add_field(
                name="Backup",
                value="\n".join([self._format_event(event) for event in result.backup]),
            )

        await ctx.send(embeds=embed, ephemeral=True)

    @staticmethod
    def _format_event(event: LfgOutputModel) -> str:
        """Format the event"""

        # get the link
        link = (
            f"[View Event](https://canary.discord.com/channels/{event.guild_id}/{event.channel_id}/{event.message_id}) - "
            if event.message_id
            else None
        )

        return f"""{link if link else ""}ID `{event.id}` - {event.activity} - {Timestamp.fromdatetime(event.start_time).format(style=TimestampStyles.ShortDateTime)}"""


def setup(client):
    LfgJoined(client)
