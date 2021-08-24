from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_choice, create_option

from ElevatorBot.commandHelpers.optionTemplates import get_user_option


class LfgBlacklist(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_subcommand(
        base="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        name="blacklist",
        description="(Un-) Blacklist a user from your own lfg event",
        options=[
            create_option(
                name="action",
                description="If you want to add to or _delete from the Blacklist",
                option_type=3,
                required=True,
                choices=[
                    create_choice(name="Blacklist", value="Blacklist"),
                    create_choice(name="Un-Blacklist", value="Un-Blacklist"),
                ],
            ),
            get_user_option(description="The user you want to add / _delete", required=True),
        ],
    )
    async def _blacklist(self, ctx: SlashContext, action, user):
        pass


def setup(client):
    client.add_cog(LfgBlacklist(client))
