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
