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
                error_codes_and_responses["DiscordIdNotFound"].format(discord_member=discord_member),
            ),
        )
        return True
    return False


async def respond_destiny_id_unknown(ctx: SlashContext, destiny_id: int, hidden: bool = True) -> bool:
    """Respond to the given context"""

    if not ctx.responded:
        await ctx.send(
            hidden=hidden,
            embed=embed_message(
                "Error",
                error_codes_and_responses["DestinyIdNotFound"].format(destiny_id=destiny_id),
            ),
        )
        return True
    return False


async def respond_invalid_time_input(ctx: SlashContext, hidden: bool = True) -> bool:
    """Respond to the given context"""

    if not ctx.responded:
        await ctx.send(
            hidden=hidden,
            embed=embed_message(
                "Error", "There was an error with the formatting of the time parameters. Please try again"
            ),
        )
        return True
    return False


async def respond_time_input_in_past(ctx: SlashContext, hidden: bool = True) -> bool:
    """Respond to the given context"""

    if not ctx.responded:
        await ctx.send(
            hidden=hidden,
            embed=embed_message("Error", "The event cannot start in the past. Please try again"),
        )
        return True
    return False


async def respond_timeout(message: discord.Message = None, hidden: bool = True):
    """Respond to the given context"""

    await message.edit(
        hidden=hidden,
        embed=embed_message(
            "Error",
            "You took too long. If you weren't finished, please try again. \nI can give you my grandmas phone number, her doing the typing might make it a bit faster 🙃",
        ),
    )
