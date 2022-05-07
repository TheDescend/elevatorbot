from xxlimited import foo
from ElevatorBot.networking.destiny.clan import DestinyClan
from Shared.networkingSchemas.destiny.clan import DestinyClanLink, DestinyClanMembersModel, DestinyClanModel
from dis_snek import InteractionContext, Member, slash_command

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formatting import embed_message, format_timedelta
from ElevatorBot.networking.destiny.account import DestinyAccount

import asyncio, aiohttp


class EventStats(BaseScale):
    @slash_command(name="gg_rank", description="Gives you your current gg_rank")
    @default_user_option()
    async def destiny(self, ctx: InteractionContext, user: Member = None):
        member = user or ctx.author

        # get destiny info
        destiny_account = DestinyAccount(ctx=ctx, discord_member=member, discord_guild=ctx.guild)
        discord_guild = destiny_account.discord_guild
        destiny_clan = DestinyClan(ctx=ctx, discord_guild=discord_guild)
        clanmembers = await destiny_clan.get_clan_members()

        parallelization_enabler = asyncio.Semaphore(10)

        top_fireteam_score_metric_hash = "2539150057"
        ranking_metric_hash = "2850716853"
        total_medallion_metric_hash = "4017597957"

        def get_metrics(metric_dict):
            output_dict = {}
            for metricname, metrichash in {
                "top_score": top_fireteam_score_metric_hash,
                "ranking": ranking_metric_hash,
                "total_medallions": total_medallion_metric_hash,
            }.items():
                output_dict[metricname] = metric_dict[metrichash]["objectiveProgress"]["progress"]
            return output_dict

        async def get_userstats(session, url, username, sem):
            async with sem:
                async with session.get(
                    url,
                    headers={"x-api-key": "e294021b3a234537bee435d575a0e31c"},
                ) as resp:
                    response_data = (await resp.json())["Response"]["metrics"]

                    metricdata = response_data["data"]["metrics"]

                    metrics = get_metrics(metricdata)
                    return {**metrics, "username": username}

        async with aiohttp.ClientSession() as session:
            tasks = []
            for cmember in clanmembers.members:
                url = f"https://stats.bungie.net/Platform/Destiny2/{cmember.system}/Profile/{cmember.destiny_id}/?components=1100"
                tasks.append(asyncio.ensure_future(get_userstats(session, url, cmember.name, parallelization_enabler)))

            userstats = await asyncio.gather(*tasks)
            ranked_userstats = sorted(
                filter(lambda x: x["total_medallions"] != 0, userstats), key=lambda us: us["top_score"], reverse=True
            )

        embed = embed_message(
            title="Clan Ranking",
            description="All clanmembers and their GG Scores",
            footer="",
            member=member,
        )
        embed.add_field(
            name="Leaderboard", value=f"""{"**top_score**":^10}\t{"**medallions**":^15}\t{"**ranking**":^10}"""
        )
        for userstats in ranked_userstats:
            embed.add_field(
                name=userstats["username"],
                value=f"""{userstats["top_score"]:^10}\t{userstats["total_medallions"]:^15}\tTop {userstats["ranking"]:^10}%""",
            )

        await ctx.send(embeds=embed)


def setup(client):
    EventStats(client)
