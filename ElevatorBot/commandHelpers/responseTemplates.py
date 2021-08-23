import discord
from discord_slash import SlashContext

from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.errorCodesAndResponses import error_codes_and_responses


async def respond_discord_member_unknown(
    ctx: SlashContext, discord_member: discord.Member, hidden: bool = True
) -> bool:
    """Respond to the given context"""

    if not ctx.responded:
        await ctx.send(
            hidden=hidden,
            embed=embed_message(
                "Error",
                error_codes_and_responses["DiscordIdNotFound"].format(
                    discord_member=discord_member
                ),
            ),
        )
        return True
    return False


async def respond_destiny_id_unknown(
    ctx: SlashContext, destiny_id: int, hidden: bool = True
) -> bool:
    """Respond to the given context"""

    if not ctx.responded:
        await ctx.send(
            hidden=hidden,
            embed=embed_message(
                "Error",
                error_codes_and_responses["DestinyIdNotFound"].format(
                    destiny_id=destiny_id
                ),
            ),
        )
        return True
    return False
