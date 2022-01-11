import dataclasses
from typing import Optional

from anyio import create_task_group
from dis_snek.models import InteractionContext, Member, TimestampStyles

from DestinyEnums.enums import (
    DestinyActivityModeTypeEnum,
    DestinyWeaponTypeEnum,
    UsableDestinyActivityModeTypeEnum,
    UsableDestinyAmmunitionTypeEnum,
    UsableDestinyDamageTypeEnum,
)
from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.backendNetworking.destiny.activities import DestinyActivities
from ElevatorBot.backendNetworking.destiny.clan import DestinyClan
from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile
from ElevatorBot.backendNetworking.destiny.roles import DestinyRoles
from ElevatorBot.backendNetworking.destiny.weapons import DestinyWeapons
from ElevatorBot.commandHelpers.autocomplete import (
    activities,
    activities_grandmaster,
    weapons,
)
from ElevatorBot.misc.formating import embed_message, format_timedelta
from ElevatorBot.static.destinyActivities import raid_to_emblem_hash
from ElevatorBot.static.emojis import custom_emojis
from NetworkingSchemas.destiny.activities import (
    DestinyActivityInputModel,
    DestinyActivityModel,
)
from NetworkingSchemas.destiny.weapons import (
    DestinyWeaponModel,
    DestinyWeaponStatsInputModel,
)


@dataclasses.dataclass
class RankResult:
    discord_member: Member
    display_text: str = dataclasses.field(init=False, default="")
    sort_value: float = dataclasses.field(init=False, default=0)
    sort_by_ascending: bool = dataclasses.field(init=False, default=False)


@dataclasses.dataclass
class RankCommandHandler:
    clan_mode: bool
    all_leaderboards: dict

    async def handle(
        self,
        ctx: InteractionContext,
        discord_leaderboards: Optional[str] = None,
        basic_leaderboards: Optional[str] = None,
        endgame_leaderboards: Optional[str] = None,
        activity_leaderboards: Optional[str] = None,
        weapon_leaderboards: Optional[str] = None,
        activity: Optional[str] = None,
        weapon: Optional[str] = None,
        reverse: bool = False,
        user: Optional[Member] = None,
    ):
        """
        Handle both rank commands
        self.clan_mode defines who gets looked at
        """

        limit = 10

        # make sure exactly one leaderboard was input
        input_count = (
            bool(discord_leaderboards)
            + bool(basic_leaderboards)
            + bool(endgame_leaderboards)
            + bool(weapon_leaderboards)
            + bool(activity_leaderboards)
        )
        if input_count != 1:
            embed = embed_message(
                "Error", f"You need to select **exactly** one leaderboard\nYou selected `{input_count}` leaderboards"
            )
            await ctx.send(embeds=embed, ephemeral=True)
            return
        leaderboard_name = (
            discord_leaderboards
            or basic_leaderboards
            or endgame_leaderboards
            or weapon_leaderboards
            or activity_leaderboards
        )

        # make sure the activity was supplied
        if activity_leaderboards:
            if not activity:
                embed = embed_message(
                    "Error",
                    "You selected an activity leaderboard, but did not supply your sought activity\nPlease try again and input the activity with the "
                    "`activity` option",
                )
                await ctx.send(embeds=embed, ephemeral=True)
                return

            # get the actual weapon
            activity: DestinyActivityModel = activities[activity.lower()]

        # make sure the weapon was supplied
        if weapon_leaderboards:
            if not weapon:
                embed = embed_message(
                    "Error",
                    "You selected a weapon leaderboard, but did not supply your sought weapon\nPlease try again and input the weapon with the `weapon` "
                    "option",
                )
                await ctx.send(embeds=embed, ephemeral=True)
                return

            # get the actual weapon
            weapon: DestinyWeaponModel = weapons[weapon.lower()]

        member = user or ctx.author

        # get the members to gather
        # how this is done depends on if only the clan should be looked at
        clan_info = None
        discord_members: list[Member]
        if self.clan_mode:
            # get the linked clan member
            clan = DestinyClan(discord_guild=ctx.guild, ctx=ctx)
            clan_info = await clan.get_clan()
            clan_members = await clan.get_clan_members()

            # remove the clan members without a discord id
            clan_discord_members: list[Optional[Member]] = [
                await ctx.guild.get_member(clan_member.discord_id)
                for clan_member in clan_members.members
                if clan_member.discord_id
            ]
            discord_members = [discord_member for discord_member in clan_discord_members if discord_member]

            # make sure the member is in there
            if member not in discord_members:
                discord_members.append(member)

        else:
            # get all server members with a registration
            discord_members = [
                server_member
                for server_member in ctx.guild.members
                if await DestinyProfile(ctx=None, discord_member=server_member, discord_guild=ctx.guild).is_registered()
            ]

        # get all results in anyio tasks
        results: list[RankResult] = []
        async with create_task_group() as tg:
            for discord_member in discord_members:
                tg.start_soon(self._handle_member, results, ctx, discord_member, leaderboard_name, activity, weapon)

        # sort the results
        sort_by_ascending = results[0].sort_by_ascending
        if reverse:
            sort_by_ascending = not sort_by_ascending
        sorted_results: list[RankResult] = sorted(
            results, key=lambda entry: entry.sort_value, reverse=not sort_by_ascending
        )

        # make the data pretty
        embed = embed_message(
            f"{clan_info.name if clan_info else ctx.guild.name}'s Top Members - {self.all_leaderboards[leaderboard_name]}"
        )

        description = []
        if activity:
            description.extend([f"Activity: {activity.name}", "⁣"])
        if weapon:
            description.extend(
                [
                    f"Weapon: [{weapon.name}](https://www.light.gg/db/items/{weapon.reference_ids[0]})",
                    f"Weapon Type: {getattr(custom_emojis, getattr(DestinyWeaponTypeEnum, weapon.weapon_type.upper()).name.lower())} {weapon.weapon_type}",
                    f"Damage Type: {getattr(custom_emojis, getattr(UsableDestinyDamageTypeEnum, weapon.damage_type.upper()).name.lower())} "
                    f"{weapon.damage_type}",
                    f"Ammo Type: {getattr(custom_emojis, getattr(UsableDestinyAmmunitionTypeEnum, weapon.ammo_type.upper()).name.lower())} "
                    f"{weapon.ammo_type}",
                    "⁣",
                ]
            )
        if reverse:
            embed.set_footer("Reverse: True")

        # add the rankings
        found = False
        for i, result in enumerate(sorted_results):
            if i < limit:
                if result.discord_member == member:
                    found = True
                    description.append(
                        f"**{i + 1}) {result.discord_member.mention}\n{custom_emojis.enter} {result.display_text}**"
                    )

                else:
                    description.append(
                        f"{i + 1}) {result.discord_member.mention}\n{custom_emojis.enter} {result.display_text}"
                    )

            elif not found:
                if result.discord_member == member:
                    description.append("...")
                    description.append(
                        f"{i + 1}) {result.discord_member.mention}\n{custom_emojis.enter} {result.display_text}"
                    )
                    break

            else:
                break

        if not found:
            description.append(f"{member.discord_member.mention} does not have this stat.")

        embed.description = "\n".join(description)
        await ctx.send(embeds=embed)

    @staticmethod
    async def _handle_member(
        results: list[RankResult],
        ctx: InteractionContext,
        discord_member: Member,
        leaderboard_name: str,
        activity: Optional[DestinyActivityModel] = None,
        weapon: Optional[DestinyWeaponModel] = None,
    ):
        """
        Gather all clan members. Faster that way :)
        Raises RuntimeError if something went wrong
        """

        result = RankResult(discord_member=discord_member)

        # open connections
        backend_account = DestinyAccount(ctx=ctx, discord_member=discord_member, discord_guild=ctx.guild)
        backend_activities = DestinyActivities(ctx=ctx, discord_member=discord_member, discord_guild=ctx.guild)
        backend_weapons = DestinyWeapons(ctx=ctx, discord_member=discord_member, discord_guild=ctx.guild)
        backend_roles = DestinyRoles(ctx=ctx, discord_member=discord_member, discord_guild=ctx.guild)

        # handle each leaderboard differently
        match leaderboard_name:
            case "discord_roles":
                # get the stat
                roles = await backend_roles.get_missing()

                # save the stat
                missing = len(roles.acquirable)
                missing_deprecated = len(roles.deprecated)

                result.sort_value = missing
                result.display_text = f"Missing Roles: {missing:,} (+{missing_deprecated} deprecated)"

                result.sort_by_ascending = True

            case "discord_join_date":
                result.sort_value = discord_member.joined_at
                result.display_text = f"Joined: {discord_member.joined_at.format(style=TimestampStyles.ShortDateTime)}"

                result.sort_by_ascending = True

            case "basic_total_time":
                # get the stat
                stat = await backend_account.get_stat("secondsPlayed")

                # save the stat
                result.sort_value = stat.value
                result.display_text = f"Time Played: {format_timedelta(stat.value)}"

            case "basic_max_power":
                # get the stat
                stat = await backend_account.get_max_power()
                artifact = await backend_account.get_artifact_level()

                # save the stat
                result.sort_value = stat.value + artifact.value
                result.display_text = f"Max Power: {stat.value:,} (+{artifact.value:,})"

            case "basic_season_pass":
                # get the stat
                season_pass = await backend_account.get_season_pass_level()

                # save the stat
                result.sort_value = season_pass.value
                result.display_text = f"Level: {season_pass.value:,}"

            case "basic_kills":
                # get the stat
                stat = await backend_account.get_stat("kills")

                # save the stat
                result.sort_value = stat.value
                result.display_text = f"Kills: {stat.value:,}"

            case "basic_melee_kills":
                # get the stat
                stat = await backend_account.get_stat("weaponKillsMelee")

                # save the stat
                result.sort_value = stat.value
                result.display_text = f"Kills: {stat.value:,}"

            case "basic_super_kills":
                # get the stat
                stat = await backend_account.get_stat("weaponKillsSuper")

                # save the stat
                result.sort_value = stat.value
                result.display_text = f"Kills: {stat.value:,}"

            case "basic_grenade_kills":
                # get the stat
                stat = await backend_account.get_stat("weaponKillsGrenade")

                # save the stat
                result.sort_value = stat.value
                result.display_text = f"Kills: {stat.value:,}"

            case "basic_deaths":
                # get the stat
                stat = await backend_account.get_stat("deaths")

                # save the stat
                result.sort_value = stat.value
                result.display_text = f"Deaths: {stat.value:,}"

            case "basic_suicides":
                # get the stat
                stat = await backend_account.get_stat("suicides")

                # save the stat
                result.sort_value = stat.value
                result.display_text = f"Suicides: {stat.value:,}"

            case "basic_orbs":
                # get the stat
                stat = await backend_account.get_stat("orbsDropped")

                # save the stat
                result.sort_value = stat.value
                result.display_text = f"Orbs: {stat.value:,}"

            case "basic_triumphs":
                # get the stat
                stat = await backend_account.get_triumph_score()

                # save the stat
                result.sort_value = stat.lifetime_score
                result.display_text = f"Score: {stat.lifetime_score:,}"

            case "basic_active_triumphs":
                # get the stat
                stat = await backend_account.get_triumph_score()

                # save the stat
                result.sort_value = stat.active_score
                result.display_text = f"Score: {stat.active_score:,}"

            case "basic_legacy_triumphs":
                # get the stat
                stat = await backend_account.get_triumph_score()

                # save the stat
                result.sort_value = stat.legacy_score
                result.display_text = f"Score: {stat.legacy_score:,}"

            case "basic_enhancement_cores":
                # get the stat
                stat = await backend_account.get_consumable_amount(consumable_id=3853748946)

                # save the stat
                result.sort_value = stat.value
                result.display_text = f"Cores: {stat.value:,}"

            case "basic_vault_space":
                # get the stat
                stat = await backend_account.get_vault_space()

                # save the stat
                result.sort_value = stat.value
                result.display_text = f"Used Space: {stat.value:,}"

                result.sort_by_ascending = True

            case "basic_bright_dust":
                # get the stat
                stat = await backend_account.get_bright_dust()

                # save the stat
                result.sort_value = stat.value
                result.display_text = f"Dust: {stat.value:,}"

            case "basic_legendary_shards":
                # get the stat
                stat = await backend_account.get_leg_shards()

                # save the stat
                result.sort_value = stat.value
                result.display_text = f"Shards: {stat.value:,}"

            case "basic_raid_banners":
                # get the stat
                stat = await backend_account.get_consumable_amount(consumable_id=3282419336)

                # save the stat
                result.sort_value = stat.value
                result.display_text = f"Banners: {stat.value:,}"

            case "basic_forges":
                # get the stat
                stat = await backend_activities.get_activity_stats(
                    input_model=DestinyActivityInputModel(mode=DestinyActivityModeTypeEnum.FORGE.value)
                )
                afk_stats = await backend_activities.get_activity_stats(
                    input_model=DestinyActivityInputModel(
                        mode=DestinyActivityModeTypeEnum.FORGE.value, need_zero_kills=True
                    )
                )

                # save the stat
                afk_completions = afk_stats.full_completions + afk_stats.cp_completions
                result.sort_value = stat.full_completions + stat.cp_completions - afk_completions
                result.display_text = f"Forges: {result.sort_value:,} (+{afk_completions:,} AFK)"

            case "basic_afk_forges":
                # get the stat
                stat = await backend_activities.get_activity_stats(
                    input_model=DestinyActivityInputModel(
                        mode=DestinyActivityModeTypeEnum.FORGE.value, need_zero_kills=True
                    )
                )

                # save the stat
                result.sort_value = stat.full_completions + stat.cp_completions
                result.display_text = f"AFK Forges: {result.sort_value:,}"

            case "basic_catalysts":
                # get the stat
                stat = await backend_account.get_catalyst_completion()

                # save the stat
                result.sort_value = stat.completed
                result.display_text = f"Catalysts: {stat.completed:,}"

            case "endgame_raids":
                # get the stat
                stat = await backend_activities.get_activity_stats(
                    input_model=DestinyActivityInputModel(mode=UsableDestinyActivityModeTypeEnum.RAID.value)
                )

                # save the stat
                result.sort_value = stat.full_completions
                result.display_text = f"Raids: {stat.full_completions:,} ({stat.cp_completions:,} CP)"

            case "endgame_raid_time":
                # get the stat
                stat = await backend_activities.get_activity_stats(
                    input_model=DestinyActivityInputModel(mode=UsableDestinyActivityModeTypeEnum.RAID.value)
                )

                # save the stat
                result.sort_value = stat.time_spend
                result.display_text = f"Time Played: {format_timedelta(stat.time_spend)}"

            case "endgame_day_one_raids":
                # get the stat
                for raid_name, collectible_id in raid_to_emblem_hash.items():
                    collectible = await backend_account.has_collectible(collectible_id=collectible_id)

                    if collectible:
                        result.sort_value += 1

                # save the stat
                result.display_text = f"Raids: {result.sort_value:,}"

            case "endgame_gms":
                # get the stat
                stat = await backend_activities.get_activity_stats(
                    input_model=DestinyActivityInputModel(
                        activity_ids=activities_grandmaster["Grandmaster: All".lower()].activity_ids
                    )
                )

                # save the stat
                result.sort_value = stat.full_completions
                result.display_text = f"Grandmasters: {stat.full_completions:,}"

            case "endgame_gm_time":
                # get the stat
                stat = await backend_activities.get_activity_stats(
                    input_model=DestinyActivityInputModel(
                        activity_ids=activities_grandmaster["Grandmaster: All".lower()].activity_ids
                    )
                )

                # save the stat
                result.sort_value = stat.time_spend
                result.display_text = f"Time Played: {format_timedelta(stat.time_spend)}"

            case "activity_full_completions":
                # get the stat
                stat = await backend_activities.get_activity_stats(
                    input_model=DestinyActivityInputModel(activity_ids=activity.activity_ids)
                )

                # save the stat
                result.sort_value = stat.full_completions
                result.display_text = f"Completions: {stat.full_completions:,} ({stat.cp_completions:,} CP)"

            case "activity_cp_completions":
                # get the stat
                stat = await backend_activities.get_activity_stats(
                    input_model=DestinyActivityInputModel(activity_ids=activity.activity_ids)
                )

                # save the stat
                result.sort_value = stat.cp_completions
                result.display_text = f"Completions: {stat.full_completions:,} ({stat.cp_completions:,} CP)"

            case "activity_kills":
                # get the stat
                stat = await backend_activities.get_activity_stats(
                    input_model=DestinyActivityInputModel(activity_ids=activity.activity_ids)
                )

                # save the stat
                percent = (stat.precision_kills / stat.kills) * 100 if stat.kills else 0
                result.sort_value = stat.kills
                result.display_text = f"Kills: {stat.kills:,} _({round(percent, 2)}% prec)_"

            case "activity_precision_kills":
                # get the stat
                stat = await backend_activities.get_activity_stats(
                    input_model=DestinyActivityInputModel(activity_ids=activity.activity_ids)
                )

                # save the stat
                result.sort_value = stat.precision_kills
                result.display_text = f"Precision Kills: {stat.precision_kills:,}"

            case "activity_percent_precision_kills":
                # get the stat
                stat = await backend_activities.get_activity_stats(
                    input_model=DestinyActivityInputModel(activity_ids=activity.activity_ids)
                )

                # save the stat
                percent = (stat.precision_kills / stat.kills) * 100 if stat.kills else 0
                result.sort_value = percent
                result.display_text = f"% Precision Kills: {round(percent, 2)}%"

            case "activity_deaths":
                # get the stat
                stat = await backend_activities.get_activity_stats(
                    input_model=DestinyActivityInputModel(activity_ids=activity.activity_ids)
                )

                # save the stat
                result.sort_value = stat.kills
                result.display_text = f"Deaths: {stat.deaths:,}"

            case "activity_assists":
                # get the stat
                stat = await backend_activities.get_activity_stats(
                    input_model=DestinyActivityInputModel(activity_ids=activity.activity_ids)
                )

                # save the stat
                result.sort_value = stat.assists
                result.display_text = f"Assists: {stat.assists:,}"

            case "activity_time_spend":
                # get the stat
                stat = await backend_activities.get_activity_stats(
                    input_model=DestinyActivityInputModel(activity_ids=activity.activity_ids)
                )

                # save the stat
                result.sort_value = stat.time_spend
                result.display_text = f"Time Played: {format_timedelta(stat.time_spend)}"

            case "activity_fastest":
                # get the stat
                stat = await backend_activities.get_activity_stats(
                    input_model=DestinyActivityInputModel(activity_ids=activity.activity_ids)
                )

                # save the stat
                result.sort_value = stat.fastest
                result.display_text = f"Fastest Time: {format_timedelta(stat.fastest)}"

                result.sort_by_ascending = True

            case "activity_average":
                # get the stat
                stat = await backend_activities.get_activity_stats(
                    input_model=DestinyActivityInputModel(activity_ids=activity.activity_ids)
                )

                # save the stat
                result.sort_value = stat.average
                result.display_text = f"Average Time: {format_timedelta(stat.average)}"

                result.sort_by_ascending = True

            case "weapon_kills":
                # get the stat
                stat = await backend_weapons.get_weapon(
                    input_data=DestinyWeaponStatsInputModel(weapon_ids=weapon.reference_ids)
                )

                # save the stat
                percent = (stat.total_precision_kills / stat.total_kills) * 100 if stat.total_kills else 0
                result.sort_value = stat.total_kills
                result.display_text = f"Kills: {stat.total_kills:,} _({round(percent, 2)}% prec)_"

            case "weapon_precision_kills":
                # get the stat
                stat = await backend_weapons.get_weapon(
                    input_data=DestinyWeaponStatsInputModel(weapon_ids=weapon.reference_ids)
                )

                # save the stat
                result.sort_value = stat.total_precision_kills
                result.display_text = f"Precision Kills: {stat.total_precision_kills:,}"

            case "weapon_precision_kills_percent":
                # get the stat
                stat = await backend_weapons.get_weapon(
                    input_data=DestinyWeaponStatsInputModel(weapon_ids=weapon.reference_ids)
                )

                # save the stat
                percent = (stat.total_precision_kills / stat.total_kills) * 100 if stat.total_kills else 0
                result.sort_value = percent
                result.display_text = f"% Precision Kills: {round(percent, 2)}"

        results.append(result)
