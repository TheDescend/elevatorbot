import discord

# returns embeded message
"""
await message.channel.send(embed=embed_message(
    'Title',
    'Desc'
))
"""


def embed_message(title: str = "", description: str = "", footer: str = None) -> discord.Embed:
    """  Takes title description and footer and returns an discord.Embed """

    assert (title or description or footer), "Need to input either title or description or footer"

    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Colour.from_rgb(r=115, g=215, b=248),  # Descend Turquoise Blue
    )
    if footer:
        embed.set_footer(
            text=footer
        )
    return embed


def split_into_chucks_of_max_4000_characters(text_str: str = None, text_list: list = None) -> list[str]:
    """ Takes either a list of strings or a string and returns a list of strings with a max length of 4000 """

    assert (text_str or text_list), "Only one param can be chosen and one must be"

    return_list = []
    n = 4000

    if text_str:
        for return_text in [text_str[i:i + n] for i in range(0, len(text_str), n)]:
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


