from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_choice, create_option


class DayOneCompletions(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_slash(
        name="day1completions",
        description="Returns a list of everyone who has completed the specified raid on Day One",
        options=[
            create_option(
                name="raid",
                description="The name of the raid",
                option_type=3,
                required=True,
                choices=[
                    create_choice(name="Last Wish", value="Last Wish"),
                    create_choice(
                        name="Scourge of the Past", value="Scourge of the Past"
                    ),
                    create_choice(name="Crown of Sorrows", value="Crown of Sorrows"),
                    create_choice(
                        name="Garden of Salvation", value="Garden of Salvation"
                    ),
                    create_choice(name="Deep Stone Crypt", value="Deep Stone Crypt"),
                    create_choice(name="Vault of Glass", value="Vault of Glass"),
                ],
            ),
        ],
    )
    async def _day1completions(
        self,
        ctx: SlashContext,
        raid: str
    ):
        pass


def setup(
    client
):
    client.add_cog(DayOneCompletions(client))
