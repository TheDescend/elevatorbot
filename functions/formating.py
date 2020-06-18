import discord

# returns embeded message
def embed_message(title, desc, footer=None):
    embed = discord.Embed(
        title=title,
        description=desc,
        color=discord.Colour.blue()
    )
    if footer:
        embed.set_footer(
            text=footer
        )
    return embed