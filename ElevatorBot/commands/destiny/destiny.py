from dis_snek.models import InteractionContext
from dis_snek.models import Member
from dis_snek.models import slash_command

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.misc.formating import format_timedelta


class Destiny(BaseScale):
    @slash_command(name="destiny", description="Gives you various destiny stats")
    @default_user_option()
    async def _destiny(self, ctx: InteractionContext, user: Member = None):
        await ctx.defer()

        if not user:
            user = ctx.author

        # get destiny info
        destiny_profile = DestinyProfile(client=ctx.bot, discord_member=user, discord_guild=ctx.guild)
        destiny_info = await destiny_profile.from_discord_member()
        if not destiny_info:
            await destiny_info.send_error_message(ctx)
            return

        heatmap_url = (
            f"https://chrisfried.github.io/secret-scrublandeux/guardian/{destiny_info.system}/{destiny_info.destiny_id}"
        )
        destiny_account = DestinyAccount(client=ctx.bot, discord_member=user, discord_guild=ctx.guild)

        # get character infos
        characters = await destiny_account.get_character_info()
        if not characters:
            await characters.send_error_message(ctx=ctx)
            return

        # get stats
        seconds_played = await destiny_account.get_stat_by_characters(stat_name="secondsPlayed")
        if not seconds_played:
            await seconds_played.send_error_message(ctx)
            return
        power = await destiny_account.get_stat_by_characters(stat_name="highestLightLevel")
        if not power:
            await power.send_error_message(ctx)
            return
        activities_cleared = await destiny_account.get_stat_by_characters(stat_name="activitiesCleared")
        if not activities_cleared:
            await activities_cleared.send_error_message(ctx)
            return
        kills = await destiny_account.get_stat_by_characters(stat_name="kills")
        if not kills:
            await kills.send_error_message(ctx)
            return
        deaths = await destiny_account.get_stat_by_characters(stat_name="deaths")
        if not deaths:
            await deaths.send_error_message(ctx)
            return
        efficiency = await destiny_account.get_stat_by_characters(stat_name="efficiency")
        if not efficiency:
            await efficiency.send_error_message(ctx)
            return

        embed = embed_message(
            f"{user.display_name}'s Destiny Stats",
            f"**Total Playtime:** {format_timedelta(seconds=sum(seconds_played.result.values()))} \n[Click to see your heatmap]({heatmap_url})",
            "For info on achievable discord roles, type: /roles overview",
        )

        """ char info field """
        embed.add_field(name="⁣", value=f"__**Characters:**__", inline=False)
        for character in characters.result["characters"]:
            character_id = character["character_id"]

            text = f"""Playtime: {format_timedelta(seconds=seconds_played.result[character_id])} \n⁣\nPower: {power.result[character_id]:,} \nActivities: {activities_cleared.result[character_id]:,} \nKills: {kills.result[character_id]:,} \nDeaths: {deaths.result[character_id]:,} \nEfficiency: {round(efficiency.result[character_id], 2)}"""
            embed.add_field(
                name=f"""{character["character_class"]} ({character["character_race"]} / {character["character_gender"]})""",
                value=text,
                inline=True,
            )

        """ triumph info field """
        embed.add_field(name="⁣", value=f"__**Triumphs:**__", inline=False)

        # todo
        # get triumph data
        triumphs = await destiny_player.get_triumphs()
        embed.add_field(
            name="Lifetime Triumph Score",
            value=f"""{triumphs["profileRecords"]["data"]["lifetimeScore"]:,}""",
            inline=True,
        )
        embed.add_field(
            name="Active Triumph Score",
            value=f"""{triumphs["profileRecords"]["data"]["activeScore"]:,}""",
            inline=True,
        )
        embed.add_field(
            name="Legacy Triumph Score",
            value=f"""{triumphs["profileRecords"]["data"]["legacyScore"]:,}""",
            inline=True,
        )

        # todo
        # get triumph completion rate
        triumphs_data = triumphs["profileRecords"]["data"]["records"]
        triumphs_completed = 0
        triumphs_no_data = 0
        for triumph in triumphs_data.values():
            status = True
            if "objectives" in triumph:
                for part in triumph["objectives"]:
                    status &= part["complete"]
            elif "intervalObjectives" in triumph:
                for part in triumph["intervalObjectives"]:
                    status &= part["complete"]
            else:
                triumphs_no_data += 1
                continue
            if status:
                triumphs_completed += 1
        embed.add_field(
            name="Triumphs",
            value=f"{triumphs_completed} / {len(triumphs_data) - triumphs_no_data}",
            inline=True,
        )

        # todo
        # get seal completion rate
        total_seals, completed_seals = await destiny_player.get_player_seals()
        embed.add_field(
            name="Seals",
            value=f"{len(completed_seals)} / {len(total_seals)}",
            inline=True,
        )

        await ctx.send(embeds=embed)


def setup(client):
    Destiny(client)
