import asyncio

from naff import Button, ButtonStyles, slash_command
from naff.api.events import Component

from ElevatorBot.commandHelpers import autocomplete
from ElevatorBot.commandHelpers.optionTemplates import autocomplete_lore_option
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.destiny.account import DestinyAccount
from ElevatorBot.static.emojis import custom_emojis
from Shared.functions.readSettingsFile import get_setting

# =============
# Descend Only!
# =============


class DestinyTransmog(BaseModule):
    @slash_command(
        name="transmog",
        description="Changes all legendary armour to the currently equipped shader and transmog",
        dm_permission=False,
        scopes=get_setting("COMMAND_GUILD_SCOPE"),
    )
    async def set_transmog(self, ctx: ElevatorInteractionContext):
        account = DestinyAccount(ctx=ctx, discord_member=ctx.author, discord_guild=ctx.guild)

        # ask for character
        characters = await account.get_character_info()
        components = []
        for character in characters.characters:
            components.append(
                Button(
                    style=ButtonStyles.GREEN,
                    label=f"{character.character_race} {character.character_gender} {character.character_class}",
                    emoji=getattr(custom_emojis, character.character_class.lower(), None),
                    custom_id=f"transmog|{character.character_id}",
                )
            )
        embed = embed_message(
            "Transmog Changer",
            f"Please select your character. \nMake sure they have the wanted transmog equipped and wait a minute or so to let the game update that information to the api.",
            member=ctx.author,
        )
        message = await ctx.send(embeds=embed, components=components)

        # wait 60s for button press
        try:
            component: Component = await ctx.client.wait_for_component(
                components=components,
                timeout=60,
                check=lambda c: c.ctx.author == ctx.author and c.ctx.message == message,
            )
        except asyncio.TimeoutError:
            for c in components:
                c.disabled = True
            embed.description = f"_Timed Out, Please Start Again_\n⁣\n~~{embed.description}~~"

            await message.edit(components=components, embeds=embed)
            return
        else:
            character_id = int(component.ctx.custom_id.split("|")[1])
            account.ctx = None
            account.edit_message = message

            for c in components:
                c.disabled = True
            embed.description = (
                "Changing your transmog, this will take a while as bungie heavily ratelimits this route..."
            )

            await component.ctx.edit_origin(components=components, embeds=embed)

            await account.set_transmog(character_id=character_id)

            embed.description = "Transmog changed successfully!"
            await message.edit(embeds=embed)


def setup(client):
    DestinyTransmog(client)
