import aiohttp
from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from ElevatorBot.misc.formating import embed_message


class FunFact(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name="funfact", description="Very fun fun facts just for the funny fun of it")
    async def _fun_fact(self, ctx: SlashContext):
        """Very fun fun facts just for the funny fun of it"""

        url = "https://uselessfacts.jsph.pl/random.json?language=en"

        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as r:
                if r.status == 200:
                    text = (await r.json())["text"]
                else:
                    text = "Offline servers make it difficult to get fun facts :("

                await ctx.send(embed=embed_message("Did you know?", text.replace("`", "'")))


def setup(client):
    client.add_cog(FunFact(client))
