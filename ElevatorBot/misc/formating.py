from typing import Any

from dis_snek.models import Colour, Embed


def embed_message(title: str = None, description: str = None, footer: str = None) -> Embed:
    """Takes title description and footer and returns an discord.Embed"""

    assert title or description or footer, "Need to input either title or description or footer"

    embed = Embed(
        title=title,
        description=description,
        color=Colour.from_rgb(r=115, g=215, b=248),  # Descend Turquoise Blue
    )
    if footer:
        embed.set_footer(text=footer)
    return embed


def split_into_chucks_of_max_2000_characters(text_str: str = None, text_list: list[Any] = None) -> list[str]:
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


def format_timedelta(seconds: int) -> str:
    """Returns a formatted message that is displayed whenever a command wants to display a duration"""

    hours = int(seconds / (60 * 60))
    minutes = int(seconds % (60 * 60) / 60)

    return f"{hours}h {minutes}m"


def format_discord_link(guild_id: int, channel_id: int, message_id: int) -> str:
    """Format a discord hyperlink"""

    return f"https://canary.discord.com/channels/{guild_id}/{channel_id}/{message_id}"
