from typing import Optional

from naff import Member, Message, NaffUser

from ElevatorBot.discordEvents.customInteractions import (
    ElevatorComponentContext,
    ElevatorInteractionContext,
    ElevatorModalContext,
)
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.errorCodesAndResponses import error_codes_and_responses


async def something_went_wrong(ctx: ElevatorInteractionContext, hidden: bool = False) -> bool:
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


async def respond_discord_member_unknown(
    ctx: ElevatorInteractionContext, discord_member: Member, hidden: bool = False
) -> bool:
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


async def respond_destiny_id_unknown(ctx: ElevatorInteractionContext, destiny_id: int, hidden: bool = False) -> bool:
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


async def respond_invalid_time_input(ctx: ElevatorInteractionContext, hidden: bool = True) -> bool:
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


async def respond_time_input_in_past(ctx: ElevatorInteractionContext, hidden: bool = True) -> bool:
    """Respond to the given context"""

    if not ctx.responded:
        await ctx.send(
            ephemeral=hidden,
            embeds=embed_message("Error", "The start time cannot be in the past. Please try again"),
        )
        return True
    return False


async def respond_timeout(
    message: Optional[Message] = None, ctx: Optional[ElevatorInteractionContext | ElevatorModalContext] = None
):
    """Respond to the given context"""

    embed = embed_message(
        "Error",
        "You took too long. If you weren't finished, please try again. \nI can give you my grandmas phone number, her doing the typing might make it a bit faster 🙃",
    )
    if message:
        await message.edit(embeds=embed)
    elif ctx:
        await ctx.send(embeds=embed, ephemeral=True)


async def respond_wrong_channel_type(
    ctx: ElevatorInteractionContext, channel_must_be: str = "text", hidden: bool = True
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


async def respond_wrong_author(
    ctx: ElevatorInteractionContext, author_must_be: Member | NaffUser, hidden: bool = True
) -> bool:
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


async def respond_pending(ctx: ElevatorInteractionContext | ElevatorComponentContext) -> bool:
    """Respond to the given context"""

    if not ctx.responded:
        await ctx.send(
            ephemeral=True,
            embeds=embed_message(
                "Error",
                "Please pass the member screening aka accept the rules and then try again",
            ),
        )
        return True
    return False
