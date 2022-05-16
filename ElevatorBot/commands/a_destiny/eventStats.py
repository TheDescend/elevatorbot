import asyncio

import aiohttp
from anyio import create_task_group
from naff import Member, slash_command

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.base import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.destiny.account import DestinyAccount
from ElevatorBot.networking.destiny.clan import DestinyClan
from ElevatorBot.networking.errors import BackendException
from Shared.networkingSchemas import DestinyClanMemberModel


class EventStats(BaseModule):
    @slash_command(name="gg_rank", description="Gives you your current gg_rank")
    @default_user_option()
    async def destiny(self, ctx: ElevatorInteractionContext, user: Member = None):
        member = user or ctx.author

        # get destiny info
        destiny_account = DestinyAccount(ctx=ctx, discord_member=member, discord_guild=ctx.guild)
        destiny_name = await destiny_account.get_destiny_name()
        discord_guild = destiny_account.discord_guild
        destiny_clan = DestinyClan(ctx=ctx, discord_guild=discord_guild)
        clan_members = await destiny_clan.get_clan_members()

        async def get_member_stats(clan_member: DestinyClanMemberModel):
            if clan_member.discord_id:
                discord_account = await ctx.guild.fetch_member(clan_member.discord_id)
                account = DestinyAccount(ctx=ctx, discord_member=discord_account, discord_guild=ctx.guild)

                try:
                    userstats.append(
                        {
                            "username": clan_member.name,
                            "top_score": await account.get_metric(2539150057),
                            "total_medallions": await account.get_metric(4017597957),
                            "ranking": await account.get_metric(2850716853),
                        }
                    )
                except BackendException:
                    pass

        userstats: list[dict] = []
        async with create_task_group() as tg:
            for clan_member in clan_members.members:
                tg.start_soon(lambda: get_member_stats(clan_member=clan_member))

        ranked_userstats = sorted(
            filter(lambda x: x["total_medallions"] != 0, userstats), key=lambda us: us["top_score"], reverse=True
        )

        embed = embed_message(
            title="Clan Ranking",
            description="All clan members and their GG Scores",
            footer="",
            member=member,
        )
        for userstats in ranked_userstats[:12]:
            embed.add_field(
                name=userstats["username"],
                value=f"""Top Score: {userstats["top_score"]:,}\n Medallions: {userstats["total_medallions"]}\nPlacement: Top {userstats["ranking"]}%""",
                inline=True,
            )

        if destiny_name.name not in map(lambda dic: dic["username"], ranked_userstats[:10]):
            my_entry = list(filter(lambda entry: entry["username"] == destiny_name.name, ranked_userstats))
            if len(my_entry) == 0:
                print("user not found, skipping...")
            else:
                embed.add_field(
                    name=my_entry[0]["username"],
                    value=f"""{my_entry[0]["top_score"]:,}\t{my_entry[0]["total_medallions"]}\tTop {my_entry[0]["ranking"]:}%""",
                )

        await ctx.send(embeds=embed)


def setup(client):
    EventStats(client)
