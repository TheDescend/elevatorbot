from dis_snek import InteractionContext, Member, slash_command

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formatting import embed_message, format_timedelta


class Destiny(BaseScale):
    @slash_command(name="destiny", description="Gives you an overview of your Destiny 2 stats")
    @default_user_option()
    async def destiny(self, ctx: InteractionContext, user: Member = None):
        member = user or ctx.author

        # get destiny info
        destiny_profile = DestinyProfile(ctx=ctx, discord_member=member, discord_guild=ctx.guild)
        destiny_info = await destiny_profile.from_discord_member()

        heatmap_url = (
            f"https://chrisfried.github.io/secret-scrublandeux/guardian/{destiny_info.system}/{destiny_info.destiny_id}"
        )
        destiny_account = DestinyAccount(ctx=ctx, discord_member=member, discord_guild=ctx.guild)

        # get character infos
        characters = await destiny_account.get_character_info()

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
            seconds_played.update({character.character_id: result.value})

            result = await destiny_account.get_stat_by_characters(
                stat_name="highestLightLevel", character_id=character.character_id
            )
            power.update({character.character_id: result.value})

            result = await destiny_account.get_stat_by_characters(
                stat_name="activitiesCleared", character_id=character.character_id
            )
            activities_cleared.update({character.character_id: result.value})

            result = await destiny_account.get_stat_by_characters(
                stat_name="kills", character_id=character.character_id
            )
            kills.update({character.character_id: result.value})

            result = await destiny_account.get_stat_by_characters(
                stat_name="deaths", character_id=character.character_id
            )
            deaths.update({character.character_id: result.value})

            result = await destiny_account.get_stat_by_characters(
                stat_name="efficiency", character_id=character.character_id
            )
            efficiency.update({character.character_id: result.value})

        total_playtime = sum(seconds_played.values())
        embed = embed_message(
            "Destiny Stats",
            f"**Total Playtime:** {format_timedelta(seconds=total_playtime)} \n[Click to see your heatmap]({heatmap_url})",
            "For info on achievable discord roles, type: /roles missing",
            member=member,
        )

        # add char info fields
        embed.add_field(name="⁣", value="__**Characters:**__", inline=False)
        for character in characters.characters:
            character_id = character.character_id

            text = f"""Playtime: {format_timedelta(seconds=seconds_played[character_id])} ({(total_playtime / seconds_played[character_id]) * 100 if seconds_played[character_id] else 0:.0f}%)\n⁣\nPower: {int(power[character_id]):,} \nActivities: {int(activities_cleared[character_id]):,} \nKills: {int(kills[character_id]):,} \nDeaths: {int(deaths[character_id]):,} \nEfficiency: {round(efficiency[character_id], 2)}"""
            embed.add_field(
                name=f"""{character.character_class} ({character.character_race} / {character.character_gender})""",
                value=text,
                inline=True,
            )

        # add triumph info field
        embed.add_field(name="⁣", value="__**Triumphs:**__", inline=False)

        # get triumph data
        triumphs = await destiny_account.get_triumph_score()
        embed.add_field(name="Lifetime Triumph Score", value=f"{triumphs.lifetime_score:,}", inline=True)
        embed.add_field(name="Active Triumph Score", value=f"{triumphs.active_score:,}", inline=True)
        embed.add_field(name="Legacy Triumph Score", value=f"{triumphs.legacy_score:,}", inline=True)

        # add seasonal info field
        embed.add_field(name="⁣", value="__**Seasonal:**__", inline=False)

        artifact = await destiny_account.get_artifact_level()
        embed.add_field(name="Artifact Level", value=f"{int(artifact.value):,}", inline=True)
        season_pass = await destiny_account.get_season_pass_level()
        embed.add_field(name="Season Pass Level", value=f"{int(season_pass.value):,}", inline=True)

        # get seal completion rate
        seals = await destiny_account.get_seal_completion()

        embed.add_field(
            name="Seals",
            value=f"{len(seals.completed)} / {len(seals.not_completed)}",
            inline=True,
        )
        embed.add_field(
            name="Guilded Seals",
            value=f"{len(seals.guilded)} / {len(seals.not_guilded)}",
            inline=True,
        )

        await ctx.send(embeds=embed)


def setup(client):
    Destiny(client)
