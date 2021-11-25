from dis_snek.models import InteractionContext, Member, TimestampStyles, slash_command

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message


class DiscordJoinDate(BaseScale):
    """Check your join date of the discord server where you execute the command"""

    @slash_command(name="discord_join_date", description="Check when you joined this discord server")
    @default_user_option()
    async def _discord_join_date(self, ctx: InteractionContext, user: Member):
        member = user or ctx.author

        await ctx.send(
            embeds=embed_message(
                f"{user.display_name}'s Discord Join Date", member.joined_at.format(style=TimestampStyles.ShortTime)
            )
        )


def setup(client):
    DiscordJoinDate(client)
