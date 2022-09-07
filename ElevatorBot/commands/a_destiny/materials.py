from naff import Member, slash_command

from ElevatorBot.commandHelpers import autocomplete
from ElevatorBot.commandHelpers.optionTemplates import autocomplete_lore_option, default_user_option
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import add_filler_field, embed_message
from ElevatorBot.networking.destiny.account import DestinyAccount
from ElevatorBot.static.emojis import custom_emojis
from Shared.networkingSchemas import DestinyNamedValueItemModel


class DestinyMaterials(BaseModule):
    @slash_command(name="materials", description="Shows your number of Destiny 2 materials", dm_permission=False)
    @default_user_option()
    async def materials(self, ctx: ElevatorInteractionContext, user: Member = None):
        member = user or ctx.author

        backend_account = DestinyAccount(ctx=ctx, discord_member=member, discord_guild=ctx.guild)
        materials = await backend_account.get_material_amount()

        # format the result
        embed = embed_message("Materials", member=member)
        data: list[DestinyNamedValueItemModel]
        for name, data in materials.__dict__.items():
            embed.add_field(
                name=name.capitalize(),
                value="\n".join(
                    [
                        f"""{getattr(custom_emojis, "_".join(item.name.split(" ")).lower().replace("(", "").replace(")", ""), custom_emojis.question)} [{item.name}](https://www.light.gg/db/items/{item.reference_id})\n{custom_emojis.enter} **{int(item.value):,}**"""
                        for item in data
                    ]
                ),
                inline=True,
            )
        if len(embed.fields) % 3 == 0:
            add_filler_field(embed, inline=True)

        await ctx.send(embeds=embed)


def setup(client):
    DestinyMaterials(client)
