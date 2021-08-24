from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_choice, create_option

from ElevatorBot.commandHelpers.optionTemplates import get_mode_choices
from ElevatorBot.static.destinyDates import expansion_dates, season_dates


class Meta(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="meta",
        description="Displays most used weapons by clanmembers (Default: in the last 30 days)",
        options=[
            create_option(
                name="class",
                description="You can restrict the class where the weapon stats count",
                option_type=3,
                required=False,
                choices=[
                    create_choice(name="Warlock", value="2271682572"),
                    create_choice(name="Hunter", value="671679327"),
                    create_choice(name="Titan", value="3655393761"),
                ],
            ),
            create_option(
                name="expansion",
                description="You can restrict the expansion (usually a year) to look at",
                option_type=3,
                required=False,
                choices=[
                    create_choice(name=expansion[1], value=f"{expansion[0]},{expansion[1]}")
                    for expansion in expansion_dates
                ],
            ),
            create_option(
                name="season",
                description="You can restrict the season to look at",
                option_type=3,
                required=False,
                choices=[create_choice(name=season[1], value=f"{season[0]},{season[1]}") for season in season_dates],
            ),
            create_option(
                name="starttime",
                description="Format: 'DD/MM/YY' - You can restrict the time from when the weapon stats start counting",
                option_type=3,
                required=False,
            ),
            create_option(
                name="endtime",
                description="Format: 'DD/MM/YY' - You can restrict the time up until which the weapon stats count",
                option_type=3,
                required=False,
            ),
            create_option(
                name="mode",
                description="You can restrict the game mode (Default: Everything)",
                option_type=3,
                required=False,
                choices=get_mode_choices(),
            ),
            create_option(
                name="activityhash",
                description="You can restrict the activity (advanced)",
                option_type=4,
                required=False,
            ),
        ],
    )
    async def _meta(self, ctx: SlashContext, **kwargs):
        pass


def setup(client):
    client.add_cog(Meta(client))
