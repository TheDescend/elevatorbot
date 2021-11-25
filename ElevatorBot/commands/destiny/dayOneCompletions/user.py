from dis_snek.models import InteractionContext, Member, slash_command

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commandHelpers.subCommandTemplates import day1completions_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.destinyActivities import raid_to_emblem_hash


class DayOneUser(BaseScale):
    @slash_command(
        **day1completions_sub_command,
        sub_cmd_name="user",
        sub_cmd_description="Look up the Day One raid completions",
    )
    @default_user_option()
    async def _day1_user(self, ctx: InteractionContext, user: Member = None):
        member = user or ctx.author

        # might take a sec
        await ctx.defer()

        embed = embed_message(f"{member.display_name}'s Day One Completions")

        # check this members raid completions
        raid_completions = []
        destiny_player = DestinyAccount(ctx=ctx, client=ctx.bot, discord_member=member, discord_guild=ctx.guild)
        for raid_name, collectible_id in raid_to_emblem_hash.items():
            result = await destiny_player.has_collectible(collectible_id=collectible_id)
            if result is None:
                return

            if result.bool:
                raid_completions.append(raid_name)

        if not raid_completions:
            embed.description = "None yet. Maybe next raid!"

        else:
            embed.description = ", ".join(raid_completions)

        await ctx.send(embeds=embed)


def setup(client):
    DayOneUser(client)
