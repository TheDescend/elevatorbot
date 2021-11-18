from dis_snek.models import ComponentContext, InteractionContext, Member, Message

from ElevatorBot.backendNetworking.errorCodesAndResponses import (
    error_codes_and_responses,
)
from ElevatorBot.misc.formating import embed_message


async def something_went_wrong(ctx: InteractionContext, hidden: bool = False) -> bool:
    """Respond to the given context"""

    if not ctx.responded:
        await ctx.send(
            ephemeral=hidden,
            embeds=embed_message(
                "Error",
                "Sorry, something went wrong. My ~~slaves~~ volunteers are already on the hunt!",
            ),
        )
        return True
    return False


async def respond_discord_member_unknown(ctx: InteractionContext, discord_member: Member, hidden: bool = True) -> bool:
    """Respond to the given context"""

    if not ctx.responded:
        await ctx.send(
            ephemeral=hidden,
            embeds=embed_message(
                "Error",
                error_codes_and_responses["DiscordIdNotFound"].format(discord_member=discord_member),
            ),
        )
        return True
    return False


async def respond_destiny_id_unknown(ctx: InteractionContext, destiny_id: int, hidden: bool = True) -> bool:
    """Respond to the given context"""

    if not ctx.responded:
        await ctx.send(
            ephemeral=hidden,
            embeds=embed_message(
                "Error",
                error_codes_and_responses["DestinyIdNotFound"].format(destiny_id=destiny_id),
            ),
        )
        return True
    return False


async def respond_invalid_time_input(ctx: InteractionContext, hidden: bool = True) -> bool:
    """Respond to the given context"""

    if not ctx.responded:
        await ctx.send(
            ephemeral=hidden,
            embeds=embed_message(
                "Error", "There was an error with the formatting of the time parameters. Please try again"
            ),
        )
        return True
    return False


async def respond_time_input_in_past(ctx: InteractionContext, hidden: bool = True) -> bool:
    """Respond to the given context"""

    if not ctx.responded:
        await ctx.send(
            ephemeral=hidden,
            embeds=embed_message("Error", "The event cannot start in the past. Please try again"),
        )
        return True
    return False


async def respond_timeout(message: Message = None):
    """Respond to the given context"""

    await message.edit(
        embeds=embed_message(
            "Error",
            "You took too long. If you weren't finished, please try again. \nI can give you my grandmas phone number, her doing the typing might make it a bit faster 🙃",
        ),
    )


async def respond_wrong_channel_type(
    ctx: InteractionContext, channel_must_be: str = "text", hidden: bool = True
) -> bool:
    """Respond to the given context"""

    if not ctx.responded:
        await ctx.send(
            ephemeral=hidden,
            embeds=embed_message(
                "Error",
                f"The channel must be a {channel_must_be} channel\nPlease try again",
            ),
        )
        return True
    return False


async def respond_wrong_author(ctx: InteractionContext, author_must_be: Member, hidden: bool = True) -> bool:
    """Respond to the given context"""

    if not ctx.responded:
        await ctx.send(
            ephemeral=hidden,
            embeds=embed_message(
                "Error",
                f"The author of the message must be {author_must_be.mention}\nPlease try again",
            ),
        )
        return True
    return False


async def respond_pending(ctx: InteractionContext | ComponentContext) -> bool:
    """Respond to the given context"""

    if not ctx.responded:
        await ctx.send(
            ephemeral=True,
            embeds=embed_message(
                "Error",
                f"Please pass the member screening aka accept the rules and then try again",
            ),
        )
        return True
    return False
