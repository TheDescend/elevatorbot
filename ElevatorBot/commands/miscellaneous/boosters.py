from dis_snek.models import InteractionContext, Member, TimestampStyles, slash_command

from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formatting import embed_message


class Boosters(BaseScale):
    @slash_command(name="boosters", description="Prints all premium subscribers (boosters) of this discord server")
    async def boosters(self, ctx: InteractionContext):

        sorted_premium_subscribers: list[Member] = sorted(
            ctx.guild.premium_subscribers, key=lambda m: m.premium_since, reverse=True
        )

        embed = embed_message(
            "Nitro Boosters",
            ",\n".join(
                [
                    f"{member.mention} since {member.premium_since.format(TimestampStyles.ShortDateTime)}"
                    for member in sorted_premium_subscribers
                ]
            )
            or "No one is currently boosting this server",
            guild=ctx.guild,
        )

        await ctx.send(embeds=embed)


def setup(client):
    Boosters(client)
