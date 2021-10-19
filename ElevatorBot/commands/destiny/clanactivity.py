from discord.ext.commands import Cog
from discord_slash import cog_ext
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot_old.static.slashCommandOptions import choices_mode


class ClanActivity(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="clanactivity",
        description="Shows information about who from the clan plays with whom (Default: in the last 7 days)",
        options=[
            create_option(
                name="mode",
                description="You can restrict the game mode",
                option_type=3,
                required=False,
                choices=choices_mode,
            ),
            create_option(
                name="starttime",
                description="Format: 'DD/MM/YY' - You can restrict the start (lower cutoff). Note: Can break for long timespan",
                option_type=3,
                required=False,
            ),
            create_option(
                name="endtime",
                description="Format: 'DD/MM/YY' - You can restrict the end  (higher cutoff)",
                option_type=3,
                required=False,
            ),
            default_user_option(description="The name of the user you want to highlight"),
        ],
    )
    async def _clanactivity(self, ctx: SlashContext, **kwargs):
        pass


def setup(client):
    client.add_cog(ClanActivity(client))
