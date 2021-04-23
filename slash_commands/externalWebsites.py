from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

from functions.database import lookupDestinyID, lookupSystem
from functions.formating import embed_message
from functions.slashCommandFunctions import get_user_obj, get_destinyID_and_system
from static.config import GUILD_IDS
from static.slashCommandOptions import options_user


class ExternalWebsitesCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.rrsystem = {
            1: 'xb',
            2: 'ps',
            3: 'pc'
        }


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
                    create_choice(
                        name="Braytech.org",
                        value="Braytech.org"
                    ),
                    create_choice(
                        name="D2 Checklist",
                        value="D2 Checklist"
                    ),
                    create_choice(
                        name="Destiny Tracker",
                        value="Destiny Tracker"
                    ),
                    create_choice(
                        name="Dungeon Report",
                        value="Dungeon Report"
                    ),
                    create_choice(
                        name="Grandmaster Report",
                        value="Grandmaster Report"
                    ),
                    create_choice(
                        name="Nightfall Report",
                        value="Nightfall Report"
                    ),
                    create_choice(
                        name="Raid Report",
                        value="Raid Report"
                    ),
                    create_choice(
                        name="Solo Report",
                        value="Solo Report"
                    ),
                    create_choice(
                        name="Trials Report",
                        value="Trials Report"
                    ),
                    create_choice(
                        name="Triumph Report",
                        value="Triumph Report"
                    ),
                ],
            ),
            options_user()
        ]
    )
    async def _website(self, ctx: SlashContext, website, **kwargs):
        user = await get_user_obj(ctx, kwargs)
        _, destinyID, system = await get_destinyID_and_system(ctx, user)
        if not destinyID:
            return

        # get the text
        text = ""
        if website == "Solo Report":
            text = f'https://elevatorbot.ch/soloreport/{system}/{destinyID}'
        elif website == "Raid Report":
            text = f'https://raid.report/{self.rrsystem[system]}/{destinyID}'
        elif website == "Dungeon Report":
            text = f'https://dungeon.report/{self.rrsystem[system]}/{destinyID}'
        elif website == "Grandmaster Report":
            text = f'https://grandmaster.report/user/{system}/{destinyID}'
        elif website == "Nightfall Report":
            text = f'https://nightfall.report/guardian/{system}/{destinyID}'
        elif website == "Trials Report":
            text = f'https://destinytrialsreport.com/report/{system}/{destinyID}'
        elif website == "Triumph Report":
            text = f'https://triumph.report/{system}/{destinyID}'
        elif website == "Braytech.org":
            text = f'https://braytech.org/{system}/{destinyID}'
        elif website == "D2 Checklist":
            text = f'https://www.d2checklist.com/{system}/{destinyID}'
        elif website == "Destiny Tracker":
            text = f'https://destinytracker.com/destiny-2/profile/{system}/{destinyID}'

        await ctx.send(embed=embed_message(
            website,
            text
        ))


def setup(client):
    client.add_cog(ExternalWebsitesCommands(client))
