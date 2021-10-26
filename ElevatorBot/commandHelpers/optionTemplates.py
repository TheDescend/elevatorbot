from typing import Any

from dis_snek.models import OptionTypes, SlashCommandChoice, slash_option

from ElevatorBot.core.destiny.stat import stat_translation
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


def default_class_option(description: str) -> Any:
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


def default_mode_option(description: str) -> Any:
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
                SlashCommandChoice(name="Raids", value=4),
                SlashCommandChoice(name="Dungeon", value=82),
                SlashCommandChoice(name="Story (including stuff like Presage)", value=2),
                SlashCommandChoice(name="Strike", value=3),
                SlashCommandChoice(name="Nightfall", value=46),
                SlashCommandChoice(name="Everything PvE", value=7),
                SlashCommandChoice(name="Trials", value=84),
                SlashCommandChoice(name="Iron Banner", value=19),
                SlashCommandChoice(name="Everything PvP", value=5),
                SlashCommandChoice(name="Gambit", value=63),
            ],
        )(func)

    return wrapper


# todo maybe autocomplete? Needs an easy way to view all options then tho
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
