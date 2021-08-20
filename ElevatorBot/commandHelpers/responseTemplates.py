import discord
from discord_slash import SlashContext

from ElevatorBot.misc.formating import embed_message


async def respond_discord_member_unknown(ctx: SlashContext, discord_member: discord.Member, hidden: bool = True) -> bool:
    """ Respond to the given context """

    if not ctx.responded:
        await ctx.send(
            hidden=hidden,
            embed=embed_message(
                "Error",
                f"I don't possess information for {discord_member.mention} \nPlease `/register` to use my commands",
            )
        )
        return True
    return False


async def respond_destiny_id_unknown(
    ctx: SlashContext,
    destiny_id: int,
    hidden: bool = True
) -> bool:
    """ Respond to the given context """

    if not ctx.responded:
        await ctx.send(
            hidden=hidden,
            embed=embed_message(
                "Error",
                f"I don't possess information for the user with the DestinyID `{destiny_id}` \nPlease `/register` to use my commands",
            )
        )
        return True
    return False
