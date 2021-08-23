from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from ElevatorBot.misc.formating import embed_message


class Boosters(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name="boosters", description="Prints all premium subscribers")
    async def _boosters(self, ctx: SlashContext):
        """Prints all premium subscribers"""

        sorted_premium_subscribers = sorted(
            ctx.guild.premium_subscribers, key=lambda m: m.premium_since, reverse=True
        )

        embed = embed_message(
            f"{ctx.guild.name} Nitro Boosters",
            ",\n".join(
                [
                    "**"
                    + f"{m.display_name:<30}"
                    + "** since: "
                    + m.premium_since.strftime("%d/%m/%Y, %H:%M")
                    for m in sorted_premium_subscribers
                ]
            ),
        )

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Boosters(client))
