from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_choice, create_option

from ElevatorBot.commandHelpers.permissionTemplates import permissions_admin


class Channel(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="channel",
        description="Make new / replace old persistent messages",
        options=[
            create_option(
                name="channel_type",
                description="The type of the channel",
                option_type=3,
                required=True,
                choices=[
                    create_choice(name="Clan Join Request", value="clanjoinrequest"),
                    create_choice(name="Registration", value="registration"),
                    create_choice(name="Other Game Roles", value="othergameroles"),
                    create_choice(name="Steam Join Codes", value="steamjoincodes"),
                    create_choice(name="Tournament", value="tournament"),
                    create_choice(name="Member Count", value="membercount"),
                    create_choice(name="Booster Count", value="boostercount"),
                    create_choice(name="Looking For Group", value="lfg"),
                    create_choice(
                        name="LFG Voice Channel Category", value="lfgvoicecategory"
                    ),
                    create_choice(name="Bot Status", value="botstatus"),
                    create_choice(name="Increment Button", value="increment_button"),
                    create_choice(name="Bungie RSS Feed", value="rss"),
                ],
            ),
            create_option(
                name="channel",
                description="Which channel to the message should be in",
                option_type=7,
                required=True,
            ),
        ],
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _channel(self, ctx: SlashContext, channel_type, channel):
        pass


def setup(client):
    client.add_cog(Channel(client))
