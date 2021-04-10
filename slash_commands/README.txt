# This shows how to format a cog.
# To create one, add a new file and / or a new class which separating commands and making them easier to read
# The bot will automatically included every .py file and every class in it.

# The following is an example class, to show the structure


class Example(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Without defining guild_ids here, the command will take up to an hour to get processed by discord, so use that for testing
    # Can be imported with "from static.config import GUILD_IDS"
    @cog_ext.cog_slash(name="example", guild_ids=GUILD_IDS)
    async def _test(self, ctx: SlashContext):
        # If you need more than 3s for the command, defer it.
        # This lets the bot "think about it" for max 15 min.
        await ctx.defer()

        await ctx.send("example")


# The setup function below is necessary.
# When we load the cog, we use the name of the file.
def setup(client):
    client.add_cog(Example(client))
