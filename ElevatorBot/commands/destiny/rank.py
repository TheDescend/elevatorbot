import asyncio
import dataclasses
from collections import namedtuple
from typing import Optional

from dis_snek.models import (
    InteractionContext,
    Member,
    OptionTypes,
    SlashCommandChoice,
    slash_command,
    slash_option,
)

from DestinyEnums.enums import (
    DestinyWeaponTypeEnum,
    UsableDestinyAmmunitionTypeEnum,
    UsableDestinyDamageTypeEnum,
)
from ElevatorBot.backendNetworking.destiny.clan import DestinyClan
from ElevatorBot.commandHelpers.autocomplete import activities, weapons
from ElevatorBot.commandHelpers.optionTemplates import (
    autocomplete_activity_option,
    autocomplete_weapon_option,
    default_user_option,
)
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.emojis import custom_emojis
from NetworkingSchemas.destiny.activities import DestinyActivityModel
from NetworkingSchemas.destiny.clan import DestinyClanMemberModel
from NetworkingSchemas.destiny.weapons import DestinyWeaponModel


@dataclasses.dataclass
class RankResult:
    discord_member: Member
    display_text: str = dataclasses.field(init=False, default="")
    sort_value: float = dataclasses.field(init=False, default=0)
    sort_by_ascending: bool = dataclasses.field(init=False, default=False)


class Rank(BaseScale):
    discord_leaderboards = {
        "discord_roles": "Roles Earned on this Discord Server",
        "discord_join_date": "Join-Date of this Discord Server",
    }
    basic_leaderboards = {
        "basic_total_time": "Total Playtime",
        "basic_max_power": "Maximum Power Level",
        "basic_kills": "Kills",
        "basic_melee_kills": "Melee Kills",
        "basic_super_kills": "Super Kills",
        "basic_grenade_kills": "Grenade Kills",
        "basic_deaths": "Deaths",
        "basic_suicides": "Suicides",
        "basic_orbs": "Orbs of Power Generated",
        "basic_triumphs": "Triumph Score",
        "basic_active_triumphs": "Active Triumph Score",
        "basic_legacy_triumphs": "Legacy Triumph Score",
        "basic_enhancement_cores": "Enhancement Cores",
        "basic_vault_space": "Vault Space Used",
        "basic_forges": "Forges Done",
    }
    endgame_leaderboards = {
        "endgame_raids": "Raids Completed",
        "endgame_raid_time": "Raid Playtime",
        "endgame_day_one_raids": "Raids Completed on Day One",
        "endgame_gms": "Grandmaster Nightfalls Completed",
        "endgame_gm_time": "Grandmaster Nightfalls Playtime",
    }
    activity_leaderboards = {
        "activity_full_completions": "Full Activity Completions",
        "activity_cp_completions": "CP Activity Completions",
        "activity_kills": "Activity Kills",
        "activity_precision_kills": "Activity Precision Kills",
        "activity_percent_precision_kills": "Activity % Precision Kills",
        "activity_deaths": "Activity Deaths",
        "activity_assists": "Activity Assists",
        "activity_time_spend": "Activity Playtime",
        "activity_fastest": "Fastest Activity Completion Time",
        "activity_average": "Average Activity Completion Time",
    }
    weapon_leaderboards = {
        "weapon_kills": "Weapon Kills",
        "weapon_precision_kills": "Weapon Precision Kills",
        "weapon_precision_kills_percent": "Weapon % Precision Kills",
    }
    all_leaderboards = (
        discord_leaderboards | basic_leaderboards | endgame_leaderboards | activity_leaderboards | weapon_leaderboards
    )

    @slash_command(
        name="rank",
        description="Display Destiny 2 leaderboard for the linked clan. Please pick exactly one leaderboard you want to see",
    )
    @slash_option(
        name="discord_leaderboards",
        description="Leaderboards concerning this discord server. Please select **exactly** one leaderboard from all options",
        opt_type=OptionTypes.STRING,
        required=False,
        choices=[SlashCommandChoice(name=name, value=value) for value, name in discord_leaderboards.items()],
    )
    @slash_option(
        name="basic_leaderboards",
        description="Leaderboards concerning basic Destiny 2 stats. Please select **exactly** one leaderboard from all options",
        opt_type=OptionTypes.STRING,
        required=False,
        choices=[SlashCommandChoice(name=name, value=value) for value, name in basic_leaderboards.items()],
    )
    @slash_option(
        name="endgame_leaderboards",
        description="Leaderboards concerning stats in Destiny 2 endgame activities. Please select **exactly** one leaderboard from all options",
        opt_type=OptionTypes.STRING,
        required=False,
        choices=[SlashCommandChoice(name=name, value=value) for value, name in endgame_leaderboards.items()],
    )
    @slash_option(
        name="activity_leaderboards",
        description="Leaderboards concerning stats in Destiny 2 activities. Please input the sought activity in `activity`. Please select **exactly** one leaderboard from all options",
        opt_type=OptionTypes.STRING,
        required=False,
        choices=[SlashCommandChoice(name=name, value=value) for value, name in activity_leaderboards.items()],
    )
    @slash_option(
        name="weapon_leaderboards",
        description="Leaderboards concerning Destiny 2 weapon stats. Please input the sought weapon in `weapon`. Please select **exactly** one leaderboard from all options",
        opt_type=OptionTypes.STRING,
        required=False,
        choices=[SlashCommandChoice(name=name, value=value) for value, name in weapon_leaderboards.items()],
    )
    @autocomplete_activity_option(
        description="If are looking for a `activity_leaderboards`, please select the activity"
    )
    @autocomplete_weapon_option(description="If are looking for a `weapon_leaderboards`, please select the weapon")
    @slash_option(
        name="reverse",
        description="If you want to reverse the sorting: Default: False",
        opt_type=OptionTypes.BOOLEAN,
        required=False,
    )
    @default_user_option()
    async def _rank(
        self,
        ctx: InteractionContext,
        discord_leaderboards: str = None,
        basic_leaderboards: str = None,
        endgame_leaderboards: str = None,
        activity_leaderboards: str = None,
        weapon_leaderboards: str = None,
        activity: str = None,
        weapon: str = None,
        reverse: bool = False,
        user: Member = None,
    ):
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
                    "You selected an activity leaderboard, but did not supply your sought activity\nPlease try again and input the activity with the `activity` option",
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
                    "You selected a weapon leaderboard, but did not supply your sought weapon\nPlease try again and input the weapon with the `weapon` option",
                )
                await ctx.send(embeds=embed, ephemeral=True)
                return

            # get the actual weapon
            weapon: DestinyWeaponModel = weapons[weapon.lower()]

        # might take a sec
        await ctx.defer()

        # get the linked clan member
        member = user or ctx.author
        clan = DestinyClan(client=ctx.bot, discord_guild=ctx.guild, discord_member=member, ctx=ctx)
        clan_info = await clan.get_clan()
        if not clan_info:
            return
        clan_members = await clan.get_clan_members()
        if not clan_members:
            return

        # remove the clan members without a discord id
        cleaned_clan_members: list[DestinyClanMemberModel] = [
            clan_member for clan_member in clan_members.members if clan_member.discord_id
        ]

        # gather all results
        try:
            results = await asyncio.gather(
                *[
                    self.handle_member(
                        ctx=ctx,
                        clan_member=clan_member,
                        leaderboard_name=leaderboard_name,
                        activity=activity,
                        weapon=weapon,
                    )
                    for clan_member in cleaned_clan_members
                ]
            )
        except RuntimeError:
            # handle the raised errors
            return

        # sort the results
        sort_by_ascending = results[0].sort_by_ascending
        sorted_results: list[RankResult] = sorted(
            results, key=lambda entry: entry.sort_value, reverse=not sort_by_ascending
        )

        # make the data pretty
        embed = embed_message(f"Top Clan Members - {self.all_leaderboards[leaderboard_name]}")

        description = []
        if activity:
            description.extend([f"Activity: {activity.name}", "⁣"])
        if weapon:
            description.extend(
                [
                    f"Weapon: [{weapon.name}](https://www.light.gg/db/items/{weapon.reference_ids[0]})",
                    f"Weapon Type: {getattr(custom_emojis, getattr(DestinyWeaponTypeEnum, weapon.weapon_type.upper()).name.lower())} {weapon.weapon_type}",
                    f"Damage Type: {getattr(custom_emojis, getattr(UsableDestinyDamageTypeEnum, weapon.damage_type.upper()).name.lower())} {weapon.damage_type}",
                    f"Ammo Type: {getattr(custom_emojis, getattr(UsableDestinyAmmunitionTypeEnum, weapon.ammo_type.upper()).name.lower())} {weapon.ammo_type}",
                    "⁣",
                ]
            )

        # add the rankings
        found = False
        i = 0
        for result in sorted_results:
            i += 1

            if i <= limit:
                if result.discord_member == member:
                    found = True
                    description.append(
                        f"**{i}) {result.discord_member.mention}\n{custom_emojis.enter} {result.display_text}**"
                    )

                else:
                    description.append(
                        f"{i}) {result.discord_member.mention}\n{custom_emojis.enter} {result.display_text}"
                    )

            elif not found:
                if result.discord_member == member:
                    description.append("...")
                    description.append(
                        f"{i}) {result.discord_member.mention}\n{custom_emojis.enter} {result.display_text}"
                    )
                    break

            else:
                break

        if not found:
            description.append(f"{member.discord_member.mention} does not have this stat.")

        embed.description = "\n".join(description)
        await ctx.send(embeds=embed)

    @staticmethod
    async def handle_member(
        ctx: InteractionContext,
        clan_member: DestinyClanMemberModel,
        leaderboard_name: str,
        activity: Optional[DestinyActivityModel] = None,
        weapon: Optional[DestinyWeaponModel] = None,
    ) -> RankResult:
        """
        Gather all clan members. Faster that way :)
        Raises RuntimeError if something went wrong
        """

        result = RankResult(clan_member=clan_member)

        # handle each leaderboard differently
        match leaderboard_name:
            case "discord_roles":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "discord_join_date":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "basic_total_time":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "basic_max_power":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "basic_kills":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "basic_melee_kills":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "basic_super_kills":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "basic_grenade_kills":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "basic_deaths":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "basic_suicides":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "basic_orbs":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "basic_triumphs":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "basic_active_triumphs":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "basic_legacy_triumphs":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "basic_enhancement_cores":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "basic_vault_space":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "basic_forges":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "endgame_raids":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "endgame_raid_time":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "endgame_day_one_raids":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "endgame_gms":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "endgame_gm_time":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "activity_full_completions":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "activity_cp_completions":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "activity_kills":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "activity_precision_kills":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "activity_percent_precision_kills":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "activity_deaths":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "activity_assists":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "activity_time_spend":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "activity_fastest":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "activity_average":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "weapon_kills":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "weapon_precision_kills":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

            case "weapon_precision_kills_percent":
                # get the stat
                aaaaaaaaa

                # save the stat
                result.sort_value = aaaa
                result.display_text = aaaa

        return result


def setup(client):
    Rank(client)
