from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_choice, create_option

from ElevatorBot.static.timezones import timezones_dict


class LfgCreate(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_subcommand(
        base="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        name="create",
        description="Creates an LFG post",
        options=[
            create_option(
                name="start_time",
                description="Format: 'HH:MM DD/MM' - When the event is supposed to start",
                option_type=3,
                required=True,
            ),
            create_option(
                name="timezone",
                description="What timezone you are in",
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name=timezone_name,
                        value=timezone_value,
                    )
                    for timezone_name, timezone_value in timezones_dict.items()
                ],
            ),
            create_option(
                name="overwrite_max_members",
                description="You can overwrite the maximum number of people that can join your event",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def _create(
        self,
        ctx: SlashContext, ):
        pass


def setup(
    client
):
    client.add_cog(LfgCreate(client))
