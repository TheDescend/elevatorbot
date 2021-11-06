from typing import Any

from dis_snek.models import OptionTypes, SlashCommandChoice, slash_option

from DestinyEnums.enums import (
    DestinyWeaponTypeEnum,
    UsableDestinyActivityModeTypeEnum,
    UsableDestinyDamageTypeEnum,
)
from ElevatorBot.commandHelpers.autocomplete import (
    autocomplete_send_activity_name,
    autocomplete_send_weapon_name,
)
from ElevatorBot.core.destiny.stat import stat_translation
from ElevatorBot.misc.formating import capitalize_string
from ElevatorBot.static.destinyDates import expansion_dates, season_and_expansion_dates
from ElevatorBot.static.timezones import timezones_dict


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


def get_timezone_choices() -> list[SlashCommandChoice]:
    return [
        SlashCommandChoice(
            name=timezone_name,
            value=timezone_value,
        )
        for timezone_name, timezone_value in timezones_dict.items()
    ]


# Decorators:


def default_user_option(
    description: str = "The user you want to look up",
    required: bool = False,
) -> Any:
    """
    Decorator that replaces @slash_option()
    Call with `@default_user_option()`
    """

    def wrapper(func):
        return slash_option(name="user", description=description, opt_type=OptionTypes.USER, required=required)(func)

    return wrapper


def default_class_option(description: str = "Restrict the class. Default: All classes") -> Any:
    """
    Decorator that replaces @slash_option()
    Call with `@default_class_option()`
    """

    def wrapper(func):
        return slash_option(
            name="destiny_class",
            description=description,
            opt_type=OptionTypes.STRING,
            required=False,
            choices=[
                SlashCommandChoice(name="Warlock", value="Warlock"),
                SlashCommandChoice(name="Hunter", value="Hunter"),
                SlashCommandChoice(name="Titan", value="Titan"),
            ],
        )(func)

    return wrapper


def default_mode_option(description: str = "Restrict the game mode. Default: All modes") -> Any:
    """
    Decorator that replaces @slash_option()
    Call with `@default_mode_option()`
    """

    def wrapper(func):
        return slash_option(
            name="mode",
            description=description,
            opt_type=OptionTypes.INTEGER,
            required=False,
            choices=[
                SlashCommandChoice(
                    name=capitalize_string(activity_type.name),
                    value=activity_type.value,
                )
                for activity_type in UsableDestinyActivityModeTypeEnum
            ],
        )(func)

    return wrapper


# todo maybe autocomplete? Needs an easy way to view all options then tho since there are more
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
            choices=[SlashCommandChoice(name=name, value=name) for name in stat_translation],
        )(func)

    return wrapper


def default_time_option(
    description: str = "Format: `HH:MM DD/MM` - Restrict the time", name: str = "start_time", required: bool = False
) -> Any:
    """
    Decorator that replaces @slash_option()
    Call with `@default_time_option()`
    """

    def wrapper(func):
        return slash_option(
            name=name,
            description=description,
            opt_type=OptionTypes.STRING,
            required=required,
        )(func)

    return wrapper


def default_expansion_option(description: str = "Restrict the time to the expansion", required: bool = False) -> Any:
    """
    Decorator that replaces @slash_option()
    Call with `@default_expansion_option()`

    The value is formatted:
    "name: str|start_time_timestamp: int|end_time_timestamp: int"
    """

    def wrapper(func):
        return slash_option(
            name="expansion",
            description=description,
            opt_type=OptionTypes.STRING,
            required=required,
            choices=[
                SlashCommandChoice(
                    name=expansion.name,
                    value=f"{expansion.name}|{int(expansion.start.timestamp())}|{int(season_and_expansion_dates[(season_and_expansion_dates.index(expansion) + 1)].start.timestamp())}",
                )
                for expansion in expansion_dates
            ],
        )(func)

    return wrapper


def default_season_option(
    description: str = "Restrict the time to the season. Usually 3 months", required: bool = False
) -> Any:
    """
    Decorator that replaces @slash_option()
    Call with `@default_season_option()`

    The value is formatted:
    "name|start_time_timestamp|end_time_timestamp"
    """

    def wrapper(func):
        return slash_option(
            name="season",
            description=description,
            opt_type=OptionTypes.STRING,
            required=required,
            choices=[
                SlashCommandChoice(
                    name=season.name,
                    value=f"{season.name}|{int(season.start.timestamp())}|{int(season_and_expansion_dates[(season_and_expansion_dates.index(season) + 1)].start.timestamp())}",
                )
                for season in season_and_expansion_dates
            ],
        )(func)

    return wrapper


def default_weapon_type_option(
    description: str = "Restrict the weapon type is looked at", required: bool = False
) -> Any:
    """
    Decorator that replaces @slash_option()
    Call with `@default_weapon_type_option()`
    """

    def wrapper(func):
        return slash_option(
            name="weapon_type",
            description=description,
            opt_type=OptionTypes.INTEGER,
            required=required,
            choices=[
                SlashCommandChoice(
                    name=capitalize_string(weapon_type.name),
                    value=weapon_type.value,
                )
                for weapon_type in DestinyWeaponTypeEnum
            ],
        )(func)

    return wrapper


def default_damage_type_option(
    description: str = "Restrict the damage type which are looked at. Default: All types", required: bool = False
) -> Any:
    """
    Decorator that replaces @slash_option()
    Call with `@default_damage_type_option()`
    """

    def wrapper(func):
        return slash_option(
            name="damage_type",
            description=description,
            opt_type=OptionTypes.INTEGER,
            required=required,
            choices=[
                SlashCommandChoice(
                    name=capitalize_string(damage_type.name),
                    value=damage_type.value,
                )
                for damage_type in UsableDestinyDamageTypeEnum
            ],
        )(func)

    return wrapper


def autocomplete_activity_option(
    description: str = "Restrict the activity. Default: All activities", required: bool = False
) -> Any:
    """
    Decorator that replaces @slash_option()
    Call with `@autocomplete_activity_option()`
    """

    def wrapper(func):
        name = "activity"

        option = slash_option(
            name=name, description=description, opt_type=OptionTypes.STRING, required=required, autocomplete=True
        )(func)

        # register the callback
        func.autocomplete(name=name)(autocomplete_send_activity_name)

        return option

    return wrapper


def autocomplete_weapon_option(
    description: str = "Restrict the weapon. Default: All weapons", required: bool = False
) -> Any:
    """
    Decorator that replaces @slash_option()
    Call with `@autocomplete_weapon_option()`
    """

    def wrapper(func):
        name = "weapon"

        option = slash_option(
            name=name, description=description, opt_type=OptionTypes.STRING, required=required, autocomplete=True
        )(func)

        # register the callback
        func.autocomplete(name=name)(autocomplete_send_weapon_name)

        return option

    return wrapper
