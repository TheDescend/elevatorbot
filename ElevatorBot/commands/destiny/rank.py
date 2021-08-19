from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_choice, create_option

from ElevatorBot.commandHelpers.optionTemplates import get_user_option


class Rank(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_slash(
        name="rank",
        description="Display Destiny 2 leaderboard for clanmates",
        options=[
            create_option(
                name="leaderboard",
                description="The name of the leaderboard you want to see",
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name="Join-Date of this Discord Server", value="discordjoindate"
                    ),
                    create_choice(
                        name="Roles Earned on this Discord Server", value="roles"
                    ),
                    create_choice(name="Total Playtime", value="totaltime"),
                    create_choice(name="Max. Power Level", value="maxpower"),
                    create_choice(name="Vault Space Used", value="vaultspace"),
                    create_choice(name="Orbs of Power Generated", value="orbs"),
                    create_choice(name="Melee Kills", value="meleekills"),
                    create_choice(name="Super Kills", value="superkills"),
                    create_choice(name="Grenade Kills", value="grenadekills"),
                    create_choice(name="Deaths", value="deaths"),
                    create_choice(name="Suicides", value="suicides"),
                    create_choice(name="Kills", value="kills"),
                    create_choice(name="Raids Done", value="raids"),
                    create_choice(name="Raid Time", value="raidtime"),
                    create_choice(name="Grandmaster Nightfalls Done", value="gm"),
                    create_choice(name="Weapon Kills", value="weapon"),
                    create_choice(
                        name="Weapon Precision Kills", value="weaponprecision"
                    ),
                    create_choice(
                        name="% Weapon Precision Kills", value="weaponprecisionpercent"
                    ),
                    create_choice(name="Enhancement Cores", value="enhancementcores"),
                    create_choice(name="Forges Done", value="forges"),
                    create_choice(name="Active Triumph Score", value="activetriumphs"),
                    create_choice(name="Legacy Triumph Score", value="legacytriumphs"),
                    create_choice(name="Triumph Score", value="triumphs"),
                ],
            ),
            create_option(
                name="arg",
                description="Depending on which leaderboard you want to see, you might need to add an additional argument",
                option_type=3,
                required=False,
            ),
            create_option(
                name="reverse",
                description="Default: 'False' - If you want to flip the sorting",
                option_type=5,
                required=False,
            ),
            get_user_option(),
        ],
    )
    async def _rank(
        self,
        ctx: SlashContext,
        *args,
        **kwargs
    ):
        pass


def setup(
    client
):
    client.add_cog(Rank(client))
