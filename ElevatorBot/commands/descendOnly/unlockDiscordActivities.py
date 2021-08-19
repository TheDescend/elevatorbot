from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_choice, create_option


class DiscordActivity(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_slash(
        name="discordactivity",
        description="Allows you to use discord activities while in a voice channel",
        options=[
            create_option(
                name="activity",
                description="Select the activity",
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name="Youtube Together",
                        value="Youtube Together|755600276941176913",
                    ),
                    create_choice(
                        name="Betrayal.io", value="Betrayal.io|773336526917861400"
                    ),
                    create_choice(
                        name="Fishingtron.io", value="Fishingtron.io|814288819477020702"
                    ),
                    create_choice(
                        name="Poker Night", value="Poker Night|755827207812677713"
                    ),
                    create_choice(
                        name="Chess in the Park",
                        value="Chess in the Park|832012815819604009",
                    ),
                ],
            ),
        ],
    )
    async def _discordactivity(
        self,
        ctx: SlashContext,
        activity: str
    ):
        pass


def setup(
    client
):
    client.add_cog(DiscordActivity(client))
