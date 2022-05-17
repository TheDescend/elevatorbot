from naff import Member, TimestampStyles, slash_command

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message


class DiscordJoinDate(BaseModule):
    """Check your join date of the discord server where you execute the command"""

    @slash_command(
        name="discord_join_date", description="Check when you joined this discord server", dm_permission=False
    )
    @default_user_option()
    async def discord_join_date(self, ctx: ElevatorInteractionContext, user: Member = None):
        member = user or ctx.author

        await ctx.send(
            embeds=embed_message(
                "Discord Join Date", member.joined_at.format(style=TimestampStyles.ShortDateTime), member=member
            )
        )


def setup(client):
    DiscordJoinDate(client)
