from dis_snek.models import InteractionContext, Member, slash_command

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message, format_progress


class Catalysts(BaseScale):
    @slash_command(
        name="catalysts", description="Shows you Destiny 2 exotic weapon catalysts and their completion status"
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
                    format_progress(
                        name=catalyst.name,
                        completion_status=catalyst.completion_status,
                        completion_percentage=catalyst.completion_percentage,
                    )
                    for catalyst in catalysts.kinetic
                ]
            ),
            inline=False,
        )
        embed.add_field(
            name="Energy",
            value="\n".join(
                [
                    format_progress(
                        name=catalyst.name,
                        completion_status=catalyst.completion_status,
                        completion_percentage=catalyst.completion_percentage,
                    )
                    for catalyst in catalysts.energy
                ]
            ),
            inline=False,
        )
        embed.add_field(
            name="Power",
            value="\n".join(
                [
                    format_progress(
                        name=catalyst.name,
                        completion_status=catalyst.completion_status,
                        completion_percentage=catalyst.completion_percentage,
                    )
                    for catalyst in catalysts.power
                ]
            ),
            inline=False,
        )

        await ctx.send(embeds=embed)


def setup(client):
    Catalysts(client)
