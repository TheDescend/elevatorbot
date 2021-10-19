from discord.ext.commands import Cog
from discord_slash import cog_ext
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_choice
from discord_slash.utils.manage_commands import create_option

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commandHelpers.optionTemplates import get_mode_choices
from ElevatorBot.static.destinyDates import expansion_dates
from ElevatorBot.static.destinyDates import season_dates


class TopWeapons(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="topweapons",
        description="Shows your top weapon ranking with in-depth customisation",
        options=[
            create_option(
                name="weapon",
                description="If you want a specific weapon to be included on the ranking",
                option_type=3,
                required=False,
            ),
            create_option(
                name="stat",
                description="Which stat you want to see for the weapon ranking",
                option_type=3,
                required=False,
                choices=[
                    create_choice(name="Kills (default)", value="kills"),
                    create_choice(name="Precision Kills", value="precisionkills"),
                    create_choice(name="% Precision Kills", value="precisionkillspercent"),
                ],
            ),
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
                description="You can restrict the game mode where the weapon stats count",
                option_type=3,
                required=False,
                choices=get_mode_choices(),
            ),
            create_option(
                name="activityhash",
                description="You can restrict the activity where the weapon stats count (advanced)",
                option_type=4,
                required=False,
            ),
            default_user_option(),
        ],
    )
    async def _topweapons(self, ctx: SlashContext, **kwargs):
        pass


def setup(client):
    client.add_cog(TopWeapons(client))
