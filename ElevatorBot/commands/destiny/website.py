import discord
from discord.ext.commands import Cog
from discord_slash import ButtonStyle, SlashContext, cog_ext
from discord_slash.utils import manage_components
from discord_slash.utils.manage_commands import create_choice, create_option

from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile
from ElevatorBot.commandHelpers.optionTemplates import get_user_option


class Website(Cog):
    def __init__(self, client):
        self.client = client
        self.system_to_name = {
            1: "xb",
            2: "ps",
            3: "pc"
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
                    create_choice(name="Braytech.org", value="Braytech.org"),
                    create_choice(name="D2 Checklist", value="D2 Checklist"),
                    create_choice(name="Destiny Tracker", value="Destiny Tracker"),
                    create_choice(name="Dungeon Report", value="Dungeon Report"),
                    create_choice(name="Grandmaster Report", value="Grandmaster Report"),
                    create_choice(name="Nightfall Report", value="Nightfall Report"),
                    create_choice(name="Strike Report", value="Strike Report"),
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
    async def _website(self, ctx: SlashContext, website: str, user: discord.Member):
        # get destiny info
        destiny_profile = DestinyProfile(client=ctx.bot, discord_member=user, discord_guild=ctx.guild)
        destiny_player = await destiny_profile.from_discord_member()
        if not destiny_player:
            await destiny_player.send_error_message(ctx)
            return

        # get the text
        match website:
            case "Solo Report":
                text = f"https://elevatorbot.ch/soloreport/{destiny_player.system}/{destiny_player.destiny_id}"

            case "Expunge Report":
                text = f"https://elevatorbot.ch/expungereport/{self.system_to_name[destiny_player.system]}/{destiny_player.destiny_id}"

            case "Raid Report":
                text = f"https://raid.report/{self.system_to_name[destiny_player.system]}/{destiny_player.destiny_id}"

            case "Dungeon Report":
                text = f"https://dungeon.report/{self.system_to_name[destiny_player.system]}/{destiny_player.destiny_id}"

            case "Grandmaster Report":
                text = f"https://grandmaster.report/user/{destiny_player.system}/{destiny_player.destiny_id}"

            case "Nightfall Report":
                text = f"https://nightfall.report/guardian/{destiny_player.system}/{destiny_player.destiny_id}"

            case "Strike Report":
                text = f"https://strike.report/{self.system_to_name[destiny_player.system]}/{destiny_player.destiny_id}"

            case "Trials Report":
                text = f"https://destinytrialsreport.com/report/{destiny_player.system}/{destiny_player.destiny_id}"

            case "Triumph Report":
                text = f"https://triumph.report/{destiny_player.system}/{destiny_player.destiny_id}"

            case "Braytech":
                text = f"https://bray.tech/{destiny_player.system}/{destiny_player.destiny_id}"

            case "D2 Checklist":
                text = f"https://www.d2checklist.com/{destiny_player.system}/{destiny_player.destiny_id}"

            case "Destiny Tracker":
                text = f"https://destinytracker.com/destiny-2/profile/{destiny_player.system}/{destiny_player.destiny_id}"

            # Wasted on Destiny
            case _:
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
    client.add_cog(Website(client))
