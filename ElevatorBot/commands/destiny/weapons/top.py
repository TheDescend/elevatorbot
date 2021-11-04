from dis_snek.models import (
    InteractionContext,
    Member,
    OptionTypes,
    SlashCommandChoice,
    slash_command,
    slash_option,
)

from ElevatorBot.backendNetworking.destiny.weapons import DestinyWeapons
from ElevatorBot.commandHelpers.autocomplete import activities, weapons
from ElevatorBot.commandHelpers.optionTemplates import (
    autocomplete_activity_option,
    autocomplete_weapon_option,
    default_class_option,
    default_expansion_option,
    default_mode_option,
    default_season_option,
    default_time_option,
    default_user_option,
    get_mode_choices,
)
from ElevatorBot.commandHelpers.subCommandTemplates import weapons_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.helperFunctions import parse_datetime_options
from ElevatorBot.static.destinyDates import expansion_dates, season_dates


class WeaponsTop(BaseScale):
    @slash_command(**weapons_sub_command, name="top", description="Shows your top weapon ranking")
    @slash_option(
        name="stat",
        description="Which stat you want the leaderboard to consider",
        required=True,
        opt_type=OptionTypes.STRING,
        choices=[
            SlashCommandChoice(name="Kills (default)", value="kills"),
            SlashCommandChoice(name="Precision Kills", value="precision_kills"),
            SlashCommandChoice(name="% Precision Kills", value="precision_kills_percent"),
        ],
    )
    @autocomplete_weapon_option(description="If you want a specific weapon to be included in the ranking")
    @default_mode_option(description="Restrict the game mode where the weapon stats count. Default: All modes")
    @autocomplete_activity_option(
        description="Restrict the activity where the weapon stats count. Overwrites `mode`. Default: All modes"
    )
    @default_class_option(description="Restrict the class where the weapon stats count. Default: All classes")
    @default_expansion_option(description="Restrict the expansion where the weapon stats count")
    @default_season_option(description="Restrict the season where the weapon stats count")
    @default_time_option(
        name="start_time",
        description="Format: `HH:MM DD/MM` - Input the **earliest** date you want the weapon stats for. Default: Jesus's Birth",
    )
    @default_time_option(
        name="end_time",
        description="Format: `HH:MM DD/MM` - Input the **latest** date you want the weapon stats for. Default: Now",
    )
    @default_user_option()
    async def _top_weapons(
        self,
        ctx: InteractionContext,
        stat: str,
        weapon: str = None,
        mode: int = None,
        activity: str = None,
        destiny_class: str = None,
        expansion: str = None,
        season: str = None,
        start_time: str = None,
        end_time: str = None,
        user: Member = None,
    ):
        # parse start and end time
        start_time, end_time = parse_datetime_options(
            ctx=ctx, expansion=expansion, season=season, start_time=start_time, end_time=end_time
        )
        if not start_time:
            return

        # get the actual weapon / activities
        if weapon:
            weapon = weapons[weapon.lower()]
        if activity:
            activity = activities[activity.lower()]

        # might take a sec
        await ctx.defer()

        member = user or ctx.author
        backend_weapons = DestinyWeapons(ctx=ctx, client=ctx.bot, discord_member=member, discord_guild=ctx.guild)


def setup(client):
    WeaponsTop(client)
