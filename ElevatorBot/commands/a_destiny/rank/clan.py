from dis_snek import InteractionContext, Member, OptionTypes, SlashCommandChoice, slash_command, slash_option

from ElevatorBot.commandHelpers.autocomplete import autocomplete_send_activity_name, autocomplete_send_weapon_name
from ElevatorBot.commandHelpers.optionTemplates import (
    autocomplete_activity_option,
    autocomplete_weapon_option,
    default_user_option,
)
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.rank import RankCommandHandler


class RankClan(BaseScale):
    clan_mode = True

    discord_leaderboards = {
        "discord_roles": "Roles Earned on this Discord Server",
        "discord_join_date": "Join-Date of this Discord Server",
    }
    basic_leaderboards = {
        "basic_total_time": "Total Playtime",
        "basic_max_power": "Maximum Power Level",
        "basic_season_pass": "Maximum Season Pass Level",
        "basic_kills": "Kills",
        "basic_melee_kills": "Kills with: Melee",
        "basic_super_kills": "Kills with: Super",
        "basic_grenade_kills": "Kills with: Grenade",
        "basic_deaths": "Deaths",
        "basic_suicides": "Suicides",
        "basic_orbs": "Orbs of Power Generated",
        "basic_triumphs": "Triumph Score",
        "basic_active_triumphs": "Active Triumph Score",
        "basic_legacy_triumphs": "Legacy Triumph Score",
        "basic_enhancement_cores": "Enhancement Cores",
        "basic_vault_space": "Vault Space Used",
        "basic_bright_dust": "Bright Dust Owned",
        "basic_legendary_shards": "Legendary Shards Owned",
        "basic_raid_banners": "Raid Banners Owned",
        "basic_forges": "Forges Done",
        "basic_afk_forges": "AFK Forges Done",
        "basic_catalysts": "Weapon Catalysts Completed",
    }
    endgame_leaderboards = {
        "endgame_raids": "Raids Completed",
        "endgame_raid_time": "Raid Playtime",
        "endgame_day_one_raids": "Raids Completed on Day One",
        "endgame_gms": "Grandmaster Nightfalls Completed",
        "endgame_gm_time": "Grandmaster Nightfalls Playtime",
    }
    activity_leaderboards = {
        "activity_full_completions": "Full Activity Completions",
        "activity_cp_completions": "CP Activity Completions",
        "activity_kills": "Activity Kills",
        "activity_precision_kills": "Activity Precision Kills",
        "activity_percent_precision_kills": "Activity % Precision Kills",
        "activity_deaths": "Activity Deaths",
        "activity_assists": "Activity Assists",
        "activity_time_spend": "Activity Playtime",
        "activity_fastest": "Fastest Activity Completion Time",
        "activity_average": "Average Activity Completion Time",
    }
    weapon_leaderboards = {
        "weapon_kills": "Weapon Kills",
        "weapon_precision_kills": "Weapon Precision Kills",
        "weapon_precision_kills_percent": "Weapon % Precision Kills",
    }
    all_leaderboards = (
        discord_leaderboards | basic_leaderboards | endgame_leaderboards | activity_leaderboards | weapon_leaderboards
    )

    @slash_command(
        name="rank",
        description="Display Destiny 2 leaderboards. Pick **only** one leaderboard from all options",
        sub_cmd_name="clan",
        sub_cmd_description="Only show clan members on the leaderboard",
    )
    @slash_option(
        name="discord_leaderboards",
        description="Leaderboards concerning this discord server",
        opt_type=OptionTypes.STRING,
        required=False,
        choices=[SlashCommandChoice(name=name, value=value) for value, name in discord_leaderboards.items()],
    )
    @slash_option(
        name="basic_leaderboards",
        description="Leaderboards concerning basic Destiny 2 stats",
        opt_type=OptionTypes.STRING,
        required=False,
        choices=[SlashCommandChoice(name=name, value=value) for value, name in basic_leaderboards.items()],
    )
    @slash_option(
        name="endgame_leaderboards",
        description="Leaderboards concerning stats in Destiny 2 endgame activities",
        opt_type=OptionTypes.STRING,
        required=False,
        choices=[SlashCommandChoice(name=name, value=value) for value, name in endgame_leaderboards.items()],
    )
    @slash_option(
        name="activity_leaderboards",
        description="Leaderboards concerning stats in Destiny 2 activities. Input the sought activity in `activity`",
        opt_type=OptionTypes.STRING,
        required=False,
        choices=[SlashCommandChoice(name=name, value=value) for value, name in activity_leaderboards.items()],
    )
    @slash_option(
        name="weapon_leaderboards",
        description="Leaderboards concerning Destiny 2 weapon stats. Input the sought weapon in `weapon`",
        opt_type=OptionTypes.STRING,
        required=False,
        choices=[SlashCommandChoice(name=name, value=value) for value, name in weapon_leaderboards.items()],
    )
    @autocomplete_activity_option(
        description="If are looking for a `activity_leaderboards`, please select the activity"
    )
    @autocomplete_weapon_option(description="If are looking for a `weapon_leaderboards`, please select the weapon")
    @slash_option(
        name="reverse",
        description="If you want to reverse the sorting: Default: False",
        opt_type=OptionTypes.BOOLEAN,
        required=False,
    )
    @default_user_option()
    async def rank(
        self,
        ctx: InteractionContext,
        discord_leaderboards: str = None,
        basic_leaderboards: str = None,
        endgame_leaderboards: str = None,
        activity_leaderboards: str = None,
        weapon_leaderboards: str = None,
        activity: str = None,
        weapon: str = None,
        reverse: bool = False,
        user: Member = None,
    ):
        handler = RankCommandHandler(clan_mode=self.clan_mode, all_leaderboards=self.all_leaderboards)
        await handler.handle(
            ctx=ctx,
            discord_leaderboards=discord_leaderboards,
            basic_leaderboards=basic_leaderboards,
            endgame_leaderboards=endgame_leaderboards,
            activity_leaderboards=activity_leaderboards,
            weapon_leaderboards=weapon_leaderboards,
            activity=activity,
            weapon=weapon,
            reverse=reverse,
            user=user,
        )


def setup(client):
    command = RankClan(client)

    # register the autocomplete callback
    command.rank.autocomplete("weapon")(autocomplete_send_weapon_name)
    command.rank.autocomplete("activity")(autocomplete_send_activity_name)
