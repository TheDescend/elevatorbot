from dis_snek import InteractionContext, slash_command

from ElevatorBot.backendNetworking.destiny.clan import DestinyClan
from ElevatorBot.commandHelpers.subCommandTemplates import setup_sub_command, setup_sub_command_clan_group
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formatting import embed_message


class ClanLink(BaseScale):
    """
    Links your own Destiny 2 clan with the discord server this was executed in
    """

    # todo perms
    @slash_command(
        **setup_sub_command,
        **setup_sub_command_clan_group,
        sub_cmd_name="link",
        sub_cmd_description="Links your own Destiny 2 clan with this discord",
    )
    async def link(self, ctx: InteractionContext):
        if ctx.author.id != 238388130581839872:
            await ctx.send(
                "This is blocked for now, since it it waiting for a vital unreleased discord feature", ephemeral=True
            )
            return

        clan = DestinyClan(ctx=ctx, discord_guild=ctx.guild)
        result = await clan.link(linked_by=ctx.author)

        await ctx.send(
            embeds=embed_message(
                "Success",
                f"This discord server has been successfully linked to the clan `{result.clan_name}`",
            )
        )


def setup(client):
    ClanLink(client)
