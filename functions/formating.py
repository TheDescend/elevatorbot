import discord

# returns embeded message
"""
await message.channel.send(embed=embed_message(
    'Title',
    'Desc'
))
"""
def embed_message(title, desc="", footer=None):
    embed = discord.Embed(
        title=title,
        description=desc,
        color=discord.Colour.blue(),
    )
    if footer:
        embed.set_footer(
            text=footer
        )
    return embed