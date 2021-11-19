import asyncio

from dis_snek.models import (
    ActionRow,
    Button,
    ButtonStyles,
    ComponentContext,
    InteractionContext,
    Member,
    Message,
    OptionTypes,
    Timestamp,
    TimestampStyles,
    slash_command,
    slash_option,
)

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.backendNetworking.destiny.lfgSystem import DestinyLfgSystem
from ElevatorBot.commandHelpers.optionTemplates import (
    default_time_option,
    default_user_option,
    get_timezone_choices,
)
from ElevatorBot.commandHelpers.responseTemplates import respond_timeout
from ElevatorBot.commandHelpers.subCommandTemplates import lfg_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.lfgSystem import LfgMessage
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.misc.helperFunctions import parse_string_datetime
from ElevatorBot.static.destinyActivities import dungeons, raids


class Catalysts(BaseScale):
    @slash_command(
        name="catalysts", description="Shows you Destiny 2 exotic weapon catalysts and your completion status"
    )
    @default_user_option()
    async def _catalysts(self, ctx: InteractionContext, user: Member = None):
        member = user or ctx.author

        account = DestinyAccount(ctx=ctx, client=ctx.bot, discord_member=member, discord_guild=ctx.guild)
        catalysts = await account.get_catalyst_completion()
        if not catalysts:
            return

        embed = embed_message(f"{member.display_name}'s Weapon Catalysts")

        # sort them by slot
        embed.add_field(
            name="Kinetic",
            value="\n".join(
                [
                    f"{catalyst.name}   |   {catalyst.completion_status}  {int(catalyst.completion_percentage * 100)}%"
                    for catalyst in catalysts.kinetic
                ]
            ),
            inline=False,
        )
        embed.add_field(
            name="Energy",
            value="\n".join(
                [
                    f"{catalyst.name}   |   {catalyst.completion_status}  {int(catalyst.completion_percentage * 100)}%"
                    for catalyst in catalysts.energy
                ]
            ),
            inline=False,
        )
        embed.add_field(
            name="Power",
            value="\n".join(
                [
                    f"{catalyst.name}   |   {catalyst.completion_status}  {int(catalyst.completion_percentage * 100)}%"
                    for catalyst in catalysts.power
                ]
            ),
            inline=False,
        )

        await ctx.send(embeds=embed)


def setup(client):
    Catalysts(client)
