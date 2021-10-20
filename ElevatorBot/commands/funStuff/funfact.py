import aiohttp
from dis_snek.models import InteractionContext
from dis_snek.models import slash_command

from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message


class FunFact(BaseScale):
    @slash_command(name="funfact", description="Very fun fun facts just for the funny fun of it")
    async def _fun_fact(self, ctx: InteractionContext):

        url = "https://uselessfacts.jsph.pl/random.json?language=en"

        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as r:
                if r.status == 200:
                    text = (await r.json())["text"]
                else:
                    text = "Offline servers make it difficult to get fun facts :("

                await ctx.send(embeds=embed_message("Did you know?", text.replace("`", "'")))


def setup(client):
    FunFact(client)
