from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_choice, create_option

from ElevatorBot.commandHelpers.optionTemplates import get_user_option


class Website(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="website",
        description="Gets your personalised link to a bunch of Destiny 2 related websites",
        options=[
            create_option(
                name="website",
                description="The name of the website you want a personalised link for",
                option_type=3,
                required=True,
                choices=[
                    create_choice(name="Braytech.org", value="Braytech.org"),
                    create_choice(name="D2 Checklist", value="D2 Checklist"),
                    create_choice(name="Destiny Tracker", value="Destiny Tracker"),
                    create_choice(name="Dungeon Report", value="Dungeon Report"),
                    create_choice(
                        name="Grandmaster Report", value="Grandmaster Report"
                    ),
                    create_choice(name="Nightfall Report", value="Nightfall Report"),
                    create_choice(name="Raid Report", value="Raid Report"),
                    create_choice(name="Solo Report", value="Solo Report"),
                    create_choice(name="Expunge Report", value="Expunge Report"),
                    create_choice(name="Trials Report", value="Trials Report"),
                    create_choice(name="Triumph Report", value="Triumph Report"),
                    create_choice(name="Wasted on Destiny", value="Wasted on Destiny"),
                ],
            ),
            get_user_option(),
        ],
    )
    async def _website(self, ctx: SlashContext, website, **kwargs):
        pass


def setup(client):
    client.add_cog(Website(client))
