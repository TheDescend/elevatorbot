from dis_snek.models import InteractionContext
from dis_snek.models import Member
from dis_snek.models import slash_command

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message


class Solos(BaseScale):
    @slash_command(name="solos", description="Shows you an overview of your Destiny 2 solo activity completions")
    @default_user_option()
    async def _solos(self, ctx: InteractionContext, user: Member):

        await ctx.defer()
        account = DestinyAccount(client=ctx.bot, discord_member=user, discord_guild=ctx.guild)

        # get the solo data
        solos = await account.get_solos()
        if not solos:
            await solos.send_error_message(ctx=ctx)
            return

        # start building the return embed
        embed = embed_message(f"{user.display_name}'s Destiny Solos")

        # add the fields
        for solo_data in solos.result["solos"]:
            embed.add_field(
                name=solo_data["activity_name"],
                value=f"""Solo Completions: **{solo_data["count"]}**\nSolo Flawless Count: **{solo_data["flawless_count"]}**\nFastest Solo: **{solo_data["fastest"]}**""",
                inline=True,
            )

        # add a pity description
        if not solos.result["solos"]:
            embed.description = "You do not seem to have any notable solo completions"

        await ctx.send(embeds=embed)


def setup(client):
    Solos(client)
