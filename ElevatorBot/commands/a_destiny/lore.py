from dis_snek import InteractionContext, slash_command

from ElevatorBot.commandHelpers.autocomplete import autocomplete_send_lore_name, lore
from ElevatorBot.commandHelpers.optionTemplates import autocomplete_lore_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formatting import embed_message


class DestinyLore(BaseScale):
    @slash_command(name="lore", description="Shows you Destiny 2 lore")
    @autocomplete_lore_option()
    async def lore(self, ctx: InteractionContext, name: str):
        # get the lore item
        lore_item = lore[name]

        embed = embed_message(
            f"Lore: {lore_item.name}",
            lore_item.description.replace("\n", "⁣\n") if lore_item.description != "" else "_No Text Available_",
        )
        if lore_item.redacted:
            embed.set_footer("This is still redacted and thus only visible to you")

        await ctx.send(embeds=embed, ephemeral=lore_item.redacted)


def setup(client):
    command = DestinyLore(client)

    # register the autocomplete callback
    command.lore.autocomplete("name")(autocomplete_send_lore_name)
