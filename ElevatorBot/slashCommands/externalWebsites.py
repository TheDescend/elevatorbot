from discord.ext import commands
from discord_slash import cog_ext, SlashContext, ButtonStyle
from discord_slash.utils import manage_components
from discord_slash.utils.manage_commands import create_option, create_choice

from ElevatorBot.functions.destinyPlayer import DestinyPlayer
from ElevatorBot.functions.slashCommandFunctions import get_user_obj
from ElevatorBot.static.slashCommandOptions import options_user


class ExternalWebsitesCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.rrsystem = {1: "xb", 2: "ps", 3: "pc"}

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
            options_user(),
        ],
    )
    async def _website(self, ctx: SlashContext, website, **kwargs):
        user = await get_user_obj(ctx, kwargs)
        destiny_player = await DestinyPlayer.from_discord_id(user.id, ctx=ctx)
        if not destiny_player:
            return

        # get the text
        text = ""
        if website == "Solo Report":
            text = f"https://elevatorbot.ch/soloreport/{destiny_player.system}/{destiny_player.destiny_id}"
        elif website == "Expunge Report":
            text = f"https://elevatorbot.ch/expungereport/{self.rrsystem[destiny_player.system]}/{destiny_player.destiny_id}"
        elif website == "Raid Report":
            text = f"https://raid.report/{self.rrsystem[destiny_player.system]}/{destiny_player.destiny_id}"
        elif website == "Dungeon Report":
            text = f"https://dungeon.report/{self.rrsystem[destiny_player.system]}/{destiny_player.destiny_id}"
        elif website == "Grandmaster Report":
            text = f"https://grandmaster.report/user/{destiny_player.system}/{destiny_player.destiny_id}"
        elif website == "Nightfall Report":
            text = f"https://nightfall.report/guardian/{destiny_player.system}/{destiny_player.destiny_id}"
        elif website == "Trials Report":
            text = f"https://destinytrialsreport.com/report/{destiny_player.system}/{destiny_player.destiny_id}"
        elif website == "Triumph Report":
            text = f"https://triumph.report/{destiny_player.system}/{destiny_player.destiny_id}"
        elif website == "Braytech.org":
            text = f"https://braytech.org/{destiny_player.system}/{destiny_player.destiny_id}"
        elif website == "D2 Checklist":
            text = f"https://www.d2checklist.com/{destiny_player.system}/{destiny_player.destiny_id}"
        elif website == "Destiny Tracker":
            text = f"https://destinytracker.com/destiny-2/profile/{destiny_player.system}/{destiny_player.destiny_id}"
        elif website == "Wasted on Destiny":
            text = f"https://wastedondestiny.com/{destiny_player.system}_{destiny_player.destiny_id}"

        components = [
            manage_components.create_actionrow(
                manage_components.create_button(
                    style=ButtonStyle.URL,
                    label=f"{user.display_name} - {website}",
                    url=text,
                ),
            ),
        ]
        await ctx.send(content="⁣", components=components)


def setup(client):
    client.add_cog(ExternalWebsitesCommands(client))
