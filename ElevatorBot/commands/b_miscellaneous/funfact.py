import aiohttp
from dis_snek import InteractionContext, slash_command
from orjson import orjson

from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formatting import embed_message


class FunFact(BaseScale):
    @slash_command(name="funfact", description="Get a fun fact, which most of the time is even pretty interesting")
    async def fun_fact(self, ctx: InteractionContext):

        url = "https://uselessfacts.jsph.pl/random.json?language=en"

        async with aiohttp.ClientSession(json_serialize=lambda x: orjson.dumps(x).decode()) as session:
            async with session.get(url=url) as r:
                if r.status == 200:
                    text = (await r.json())["text"]
                else:
                    text = "Offline servers make it difficult to get fun facts :("

                await ctx.send(embeds=embed_message("Did You Know?", text.replace("`", "'")))


def setup(client):
    FunFact(client)
