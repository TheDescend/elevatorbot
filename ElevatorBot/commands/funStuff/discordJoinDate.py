from dis_snek.models import InteractionContext, Member, slash_command

from ElevatorBot.commandHelpers.optionTemplates import default_user_option, misc_group
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message


class DiscordJoinDate(BaseScale):
    """Check your join date of the discord server where you execute the command"""

    @slash_command(name="discordjoindate", description="Check when you joined this discord server", **misc_group)
    @default_user_option()
    async def _discord_join_date(self, ctx: InteractionContext, user: Member):

        await ctx.send(
            embeds=embed_message(
                f"{user.display_name}'s Discord Join Date",
                f"You joined on <t:{int(user.joined_at.timestamp())}>",
            )
        )


def setup(client):
    DiscordJoinDate(client)
