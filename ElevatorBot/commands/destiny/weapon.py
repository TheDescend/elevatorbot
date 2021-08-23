from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_choice, create_option

from ElevatorBot.commandHelpers.optionTemplates import get_mode_choices, get_user_option


class Weapon(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="weapon",
        description="Shows weapon stats for the specified weapon with in-depth customisation",
        options=[
            create_option(
                name="weapon",
                description="The name of the weapon you want to see stats for",
                option_type=3,
                required=True,
            ),
            create_option(
                name="stat",
                description="Which stat you want to see for the weapon",
                option_type=3,
                required=False,
                choices=[
                    create_choice(name="Kills (default)", value="kills"),
                    create_choice(name="Precision Kills", value="precisionkills"),
                    create_choice(
                        name="% Precision Kills", value="precisionkillspercent"
                    ),
                ],
            ),
            create_option(
                name="graph",
                description="Default: 'False' - See a timeline of your weapon usage instead of an overview of key stats",
                option_type=5,
                required=False,
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
            get_user_option(),
        ],
    )
    async def _weapon(self, ctx: SlashContext, **kwargs):
        pass


def setup(client):
    client.add_cog(Weapon(client))
