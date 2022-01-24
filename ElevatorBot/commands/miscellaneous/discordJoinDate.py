from dis_snek import InteractionContext, Member, TimestampStyles, slash_command

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formatting import embed_message


class DiscordJoinDate(BaseScale):
    """Check your join date of the discord server where you execute the command"""

    @slash_command(name="discord_join_date", description="Check when you joined this discord server")
    @default_user_option()
    async def discord_join_date(self, ctx: InteractionContext, user: Member = None):
        member = user or ctx.author

        await ctx.send(
            embeds=embed_message(
                "Discord Join Date", member.joined_at.format(style=TimestampStyles.ShortDateTime), member=member
            )
        )


def setup(client):
    DiscordJoinDate(client)
