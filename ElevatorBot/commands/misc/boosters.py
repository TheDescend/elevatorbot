from dis_snek.models import InteractionContext, slash_command

from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message


class Boosters(BaseScale):
    @slash_command(name="boosters", description="Prints all premium subscribers (boosters) of this discord server")
    async def _boosters(self, ctx: InteractionContext):

        sorted_premium_subscribers = sorted(ctx.guild.premium_subscribers, key=lambda m: m.premium_since, reverse=True)

        embed = embed_message(
            f"{ctx.guild.name} Nitro Boosters",
            ",\n".join(
                [
                    "**" + f"{m.display_name:<30}" + "** since: " + m.premium_since.strftime("%d/%m/%Y, %H:%M")
                    for m in sorted_premium_subscribers
                ]
            ),
        )

        await ctx.send(embeds=embed)


def setup(client):
    Boosters(client)
