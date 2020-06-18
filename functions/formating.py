import discord

# returns embeded message
def embed_message(title, desc, footer=None):
    embed = discord.Embed(
        title=title,
        description=desc
    )
    if footer:
        embed.set_footer(
            text=footer
        )
    return embed