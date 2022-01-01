from dis_snek.models import InteractionContext, Member, slash_command

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message, format_progress


class Seals(BaseScale):
    @slash_command(
        name="seals",
        description="View all Destiny 2 seals and your completion status",
    )
    @default_user_option()
    async def seals(self, ctx: InteractionContext, user: Member = None):
        member = user or ctx.author

        destiny_profile = DestinyAccount(ctx=ctx, discord_member=member, discord_guild=ctx.guild)
        result = await destiny_profile.get_seal_completion()

        # format the message nicely
        embed = embed_message(f"{member.display_name}'s Seals")
        embed.add_field(
            name="Completed",
            value="\n".join(
                [
                    format_progress(
                        name=seal.name,
                        completion_status=seal.completion_status,
                        completion_percentage=seal.completion_percentage,
                    )
                    for seal in result.completed
                ]
            ),
            inline=False,
        )
        embed.add_field(
            name="Not Completed",
            value="\n".join(
                [
                    format_progress(
                        name=seal.name,
                        completion_status=seal.completion_status,
                        completion_percentage=seal.completion_percentage,
                    )
                    for seal in result.not_completed
                ]
            ),
            inline=False,
        )
        embed.add_field(
            name="Guilded",
            value="\n".join(
                [
                    format_progress(
                        name=seal.name,
                        completion_status=seal.completion_status,
                        completion_percentage=seal.completion_percentage,
                    )
                    for seal in result.guilded
                ]
            ),
            inline=False,
        )
        embed.add_field(
            name="Not Guilded",
            value="\n".join(
                [
                    format_progress(
                        name=seal.name,
                        completion_status=seal.completion_status,
                        completion_percentage=seal.completion_percentage,
                    )
                    for seal in result.not_guilded
                ]
            ),
            inline=False,
        )

        await ctx.send(embeds=embed)


def setup(client):
    Seals(client)
