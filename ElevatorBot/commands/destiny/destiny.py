from dis_snek.models import InteractionContext, Member, slash_command

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message, format_timedelta


class Destiny(BaseScale):
    @slash_command(name="destiny", description="Gives you various destiny stats")
    @default_user_option()
    async def _destiny(self, ctx: InteractionContext, user: Member = None):
        await ctx.defer()

        if not user:
            user = ctx.author

        # get destiny info
        destiny_profile = DestinyProfile(ctx=ctx, client=ctx.bot, discord_member=user, discord_guild=ctx.guild)
        destiny_info = await destiny_profile.from_discord_member()
        if not destiny_info:
            await destiny_info.send_error_message(ctx)
            return

        heatmap_url = (
            f"https://chrisfried.github.io/secret-scrublandeux/guardian/{destiny_info.system}/{destiny_info.destiny_id}"
        )
        destiny_account = DestinyAccount(ctx=ctx, client=ctx.bot, discord_member=user, discord_guild=ctx.guild)

        # get character infos
        characters = await destiny_account.get_character_info()
        if not characters:
            return

        seconds_played = {}
        power = {}
        activities_cleared = {}
        kills = {}
        deaths = {}
        efficiency = {}

        # get stats
        for character in characters.characters:
            result = await destiny_account.get_stat_by_characters(
                stat_name="secondsPlayed", character_id=character.character_id
            )
            if not result:
                return
            seconds_played.update({character.character_id: result.value})

            result = await destiny_account.get_stat_by_characters(
                stat_name="highestLightLevel", character_id=character.character_id
            )
            if not result:
                return
            power.update({character.character_id: result.value})

            result = await destiny_account.get_stat_by_characters(
                stat_name="activitiesCleared", character_id=character.character_id
            )
            if not result:
                return
            activities_cleared.update({character.character_id: result.value})

            result = await destiny_account.get_stat_by_characters(
                stat_name="kills", character_id=character.character_id
            )
            if not result:
                return
            kills.update({character.character_id: result.value})

            result = await destiny_account.get_stat_by_characters(
                stat_name="deaths", character_id=character.character_id
            )
            if not result:
                return
            deaths.update({character.character_id: result.value})

            result = await destiny_account.get_stat_by_characters(
                stat_name="efficiency", character_id=character.character_id
            )
            if not result:
                return
            efficiency.update({character.character_id: result.value})

        embed = embed_message(
            f"{user.display_name}'s Destiny Stats",
            f"**Total Playtime:** {format_timedelta(seconds=sum(seconds_played.values()))} \n[Click to see your heatmap]({heatmap_url})",
            "For info on achievable discord roles, type: /roles missing",
        )

        # add char info fields
        embed.add_field(name="⁣", value=f"__**Characters:**__", inline=False)
        for character in characters.characters:
            character_id = character.character_id

            text = f"""Playtime: {format_timedelta(seconds=seconds_played[character_id])} \n⁣\nPower: {power[character_id]:,} \nActivities: {activities_cleared[character_id]:,} \nKills: {kills[character_id]:,} \nDeaths: {deaths[character_id]:,} \nEfficiency: {round(efficiency[character_id], 2)}"""
            embed.add_field(
                name=f"""{character.character_class} ({character.character_race} / {character.character_gender})""",
                value=text,
                inline=True,
            )

        # add triumph info field
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
