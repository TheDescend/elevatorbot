from typing import Any

from dis_snek.models import OptionTypes
from dis_snek.models import slash_option
from dis_snek.models import SlashCommandChoice


def get_mode_choices() -> list[SlashCommandChoice]:
    return [
        SlashCommandChoice(name="Everything (Default)", value="0"),
        SlashCommandChoice(name="Raids", value="4"),
        SlashCommandChoice(name="Dungeon", value="82"),
        SlashCommandChoice(name="Story (including stuff like Presage)", value="2"),
        SlashCommandChoice(name="Strike", value="3"),
        SlashCommandChoice(name="Nightfall", value="46"),
        SlashCommandChoice(name="Everything PvE", value="7"),
        SlashCommandChoice(name="Trials", value="84"),
        SlashCommandChoice(name="Iron Banner", value="19"),
        SlashCommandChoice(name="Everything PvP", value="5"),
        SlashCommandChoice(name="Gambit", value="63"),
    ]


# Decorators:


def default_user_option(
    description: str = "The name of the user you want to look up",
    required: bool = False,
) -> Any:
    """
    Decorator that replaces @slash_option()
    Call with `@default_user_option()`
    """

    def wrapper(func):
        return slash_option(name="user", description=description, opt_type=OptionTypes.USER, required=required)(func)

    return wrapper


def default_stat_option() -> Any:
    """
    Decorator that replaces @slash_option()
    Call with `@default_stat_option()`
    """

    def wrapper(func):
        return slash_option(
            name="name",
            description="The name of the leaderboard you want to see",
            opt_type=OptionTypes.STRING,
            required=True,
            choices=[
                SlashCommandChoice(name="Kills", value="kills"),
                SlashCommandChoice(name="Precision Kills", value="precisionKills"),
                SlashCommandChoice(name="Assists", value="assists"),
                SlashCommandChoice(name="Deaths", value="deaths"),
                SlashCommandChoice(name="Suicides", value="suicides"),
                SlashCommandChoice(name="KDA", value="efficiency"),
                SlashCommandChoice(name="Longest Kill Distance", value="longestKillDistance"),
                SlashCommandChoice(name="Average Kill Distance", value="averageKillDistance"),
                SlashCommandChoice(name="Total Kill Distance", value="totalKillDistance"),
                SlashCommandChoice(name="Longest Kill Spree", value="longestKillSpree"),
                SlashCommandChoice(name="Average Lifespan", value="averageLifespan"),
                SlashCommandChoice(name="Resurrections Given", value="resurrectionsPerformed"),
                SlashCommandChoice(name="Resurrections Received", value="resurrectionsReceived"),
                SlashCommandChoice(name="Number of Players Played With", value="allParticipantsCount"),
                SlashCommandChoice(name="Longest Single Life (in s)", value="longestSingleLife"),
                SlashCommandChoice(name="Orbs of Power Dropped", value="orbsDropped"),
                SlashCommandChoice(name="Orbs of Power Gathered", value="orbsGathered"),
                SlashCommandChoice(name="Time Played (in s)", value="secondsPlayed"),
                SlashCommandChoice(name="Activities Cleared", value="activitiesCleared"),
                SlashCommandChoice(name="Public Events Completed", value="publicEventsCompleted"),
                SlashCommandChoice(name="Heroic Public Events Completed", value="heroicPublicEventsCompleted"),
                SlashCommandChoice(name="Kills with: Super", value="weaponKillsSuper"),
                SlashCommandChoice(name="Kills with: Melee", value="weaponKillsMelee"),
                SlashCommandChoice(name="Kills with: Grenade", value="weaponKillsGrenade"),
                SlashCommandChoice(name="Kills with: Ability", value="weaponKillsAbility"),
            ],
        )(func)

    return wrapper
