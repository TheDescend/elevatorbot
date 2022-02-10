import datetime
from typing import Any, Optional

from dis_snek import Colour, Embed, Guild, Member

from ElevatorBot.static.emojis import custom_emojis


def embed_message(
    title: Optional[str] = None,
    description: Optional[str] = None,
    footer: Optional[str] = None,
    member: Optional[Member] = None,
    guild: Optional[Guild] = None,
) -> Embed:
    """Takes title description and footer and returns an Embed"""

    assert (
        title is not None or description is not None or footer is not None
    ), "Need to input either title or description or footer"

    if not member or guild:
        embed = Embed(title=title, description=description, color=Colour.from_hex("#71b093"))
    else:
        embed = Embed(description=description, color=Colour.from_hex("#71b093"))
        if member:
            embed.set_author(name=f"{member.display_name}'s {title}", icon_url=member.display_avatar.url)
        elif guild:
            embed.set_author(name=f"{guild.name}'s {title}", icon_url=guild.icon.url)

    if footer:
        embed.set_footer(text=footer)
    return embed


def capitalize_string(s: str) -> str:
    """Capitalise all parts of a string divided by "_" or " " """

    split = []
    for part in s.split("_"):
        split.extend(part.split())

    return " ".join([part.capitalize() for part in split])


def un_capitalize_string(s: str) -> str:
    """Un-capitalise all parts of a string and divide them by "_" """

    split = []
    for part in s.split(" "):
        split.extend(part.split())

    return "_".join([part.lower() for part in split])


def split_into_chucks_of_max_2000_characters(
    text_str: Optional[str] = None, text_list: Optional[list[Any]] = None
) -> list[str]:
    """Takes either a list of strings or a string and returns a list of strings with a max length of 4000"""

    assert text_str or text_list, "Only one param can be chosen and one must be"

    return_list = []
    n = 2000

    if text_str:
        for return_text in [text_str[i : i + n] for i in range(0, len(text_str), n)]:
            return_list.append(return_text)
        return return_list

    elif text_list:
        return_text = ""
        for text in text_list:
            if len(return_text + str(text)) <= n:
                return_text += str(text)
            else:
                return_list.append(return_text)
                return_text = str(text)
        if return_text:
            return_list.append(return_text)
        return return_list


def format_timedelta(seconds: Optional[float | datetime.timedelta]) -> str:
    """Returns a formatted message that is displayed whenever a command wants to display a duration"""

    if seconds is None:
        return "None"

    if isinstance(seconds, datetime.timedelta):
        seconds = seconds.seconds

    minutes = seconds // 60
    hours = minutes // 60

    if hours != 0:
        return f"{hours:,}h {minutes % 60:,}m"
    else:
        return f"{minutes % 60:,}m {seconds % 60:,}s"


def replace_progress_formatting(completion_status: str) -> str:
    """Replace the letter with emojis"""

    replacements = {
        "A": str(custom_emojis.progress_zero),
        "B": str(custom_emojis.progress_zero_edge),
        "C": str(custom_emojis.progress_one_quarter),
        "D": str(custom_emojis.progress_two_quarter),
        "E": str(custom_emojis.progress_three_quarter),
        "F": str(custom_emojis.progress_four_quarter),
    }

    # replace the temp progress bar letters
    for to_replace, replace_with in replacements.items():
        completion_status = completion_status.replace(to_replace, replace_with)

    return completion_status


def format_progress(name: str, completion_status: str, completion_percentage: float) -> str:
    """Returns a formatted message that is displayed whenever a command wants to display progress message"""

    completion_status = replace_progress_formatting(completion_status)

    return f"""{completion_status} `{int(completion_percentage * 100):>3}%` **||** {name}"""


def get_emoji_from_rank(rank: int) -> str:
    """Convert the rank to the rank emoji if applicable"""

    match rank:
        case 1:
            emoji = str(custom_emojis.first_place)
        case 2:
            emoji = str(custom_emojis.second_place)
        case 3:
            emoji = str(custom_emojis.third_place)
        case _:
            emoji = f"{rank})"

    return emoji
