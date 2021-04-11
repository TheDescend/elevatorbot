# This shows how to format a cog.
# To create one, add a new file and / or a new class which separating commands and making them easier to read
# The bot will automatically included every .py file and every class in it.

# The following is an example class, to show the structure



from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from static.config import GUILD_IDS


class Example(commands.Cog):
    def __init__(self, client):
        self.client = client

    # For more info, consult - https://discord-py-slash-command.readthedocs.io/en/latest/discord_slash.cog_ext.html
    @cog_ext.cog_slash(
        name="example",
        description="Example Desc",

        # Without defining guild_ids here, the command will take up to an hour to get processed by discord, so use that for testing
        # Can be imported with - from static.config import GUILD_IDS
        guild_ids=GUILD_IDS

        # For more info, also on types, view - https://discord-py-slash-command.readthedocs.io/en/latest/gettingstarted.html
        options=[
            create_option(
                name="option",
                description="The description",
                option_type=3,
                required=False
            )
        ]
    )
    # This checks permissions, am using audit log privs for now - https://discordpy.readthedocs.io/en/latest/api.html#permissions
    @commands.has_permissions(view_audit_log=True)
    async def _test(self, ctx: SlashContext):
        # If you need more than 3s for the command, defer it.
        # This lets the bot "think about it" for max 15 min.
        await ctx.defer()

        await ctx.send("example")


# The setup function below is necessary.
# When we load the cog, we use the name of the file.
def setup(client):
    client.add_cog(Example(client))
