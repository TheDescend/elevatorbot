import datetime
from typing import Optional

from anyio import create_task_group, to_thread
from dis_snek import Embed
from dis_snek.models import Guild, InteractionContext, Timestamp, TimestampStyles, slash_command

from ElevatorBot.backendNetworking.destiny.clan import DestinyClan
from ElevatorBot.backendNetworking.destiny.weapons import DestinyWeapons
from ElevatorBot.commandHelpers.autocomplete import activities, autocomplete_send_activity_name
from ElevatorBot.commandHelpers.optionTemplates import (
    autocomplete_activity_option,
    default_class_option,
    default_damage_type_option,
    default_expansion_option,
    default_mode_option,
    default_season_option,
    default_time_option,
    default_weapon_type_option,
)
from ElevatorBot.commandHelpers.subCommandTemplates import weapons_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import capitalize_string, embed_message
from ElevatorBot.misc.helperFunctions import parse_datetime_options
from ElevatorBot.static.emojis import custom_emojis
from Shared.DestinyEnums.enums import (
    DestinyWeaponTypeEnum,
    UsableDestinyActivityModeTypeEnum,
    UsableDestinyDamageTypeEnum,
)
from Shared.NetworkingSchemas.destiny import (
    DestinyActivityModel,
    DestinyTopWeaponModel,
    DestinyTopWeaponsInputModel,
    DestinyTopWeaponsModel,
    DestinyTopWeaponsStatInputModelEnum,
)
from Shared.NetworkingSchemas.destiny.clan import DestinyClanModel


class WeaponsMeta(BaseScale):
    @slash_command(
        **weapons_sub_command,
        sub_cmd_name="meta",
        sub_cmd_description="Displays the most used Destiny 2 weapons by clan members from the linked clan",
    )
    @default_mode_option()
    @autocomplete_activity_option()
    @default_weapon_type_option()
    @default_damage_type_option()
    @default_class_option()
    @default_expansion_option()
    @default_season_option()
    @default_time_option(
        name="start_time",
        description="Format: `DD/MM/YY` - Input the **earliest** date you want the weapon stats for. Default: Big Bang",
    )
    @default_time_option(
        name="end_time",
        description="Format: `DD/MM/YY` - Input the **latest** date you want the weapon stats for. Default: Now",
    )
    async def meta(
        self,
        ctx: InteractionContext,
        mode: str = None,
        activity: str = None,
        destiny_class: str = None,
        weapon_type: int = None,
        damage_type: int = None,
        expansion: str = None,
        season: str = None,
        start_time: str = None,
        end_time: str = None,
    ):
        mode = int(mode) if mode else None

        stat = DestinyTopWeaponsStatInputModelEnum.KILLS

        # parse start and end time
        start_time, end_time = await parse_datetime_options(
            ctx=ctx, expansion=expansion, season=season, start_time=start_time, end_time=end_time
        )
        if not start_time:
            return

        # get the linked clan member
        clan = DestinyClan(discord_guild=ctx.guild, ctx=ctx)
        clan_info = await clan.get_clan()
        clan_members = await clan.get_clan_members()

        # get the actual activity
        if activity:
            activity = activities[activity.lower()]

        # get the clan members in anyio tasks
        results: list[DestinyTopWeaponsModel] = []
        async with create_task_group() as tg:
            for clan_member in clan_members.members:
                tg.start_soon(
                    self.handle_clan_member,
                    results,
                    stat,
                    clan_member.discord_id,
                    ctx.guild,
                    start_time,
                    end_time,
                    mode,
                    activity,
                    destiny_class,
                    weapon_type,
                    damage_type,
                )

        # format the message
        embed = await to_thread.run_sync(
            meta_subprocess,
            results,
            start_time,
            end_time,
            clan_info,
            mode,
            activity,
            destiny_class,
            weapon_type,
            damage_type,
        )

        await ctx.send(embeds=embed)

    @staticmethod
    async def handle_clan_member(
        results: list,
        stat: DestinyTopWeaponsStatInputModelEnum,
        discord_id: int,
        guild: Guild,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        mode: int = None,
        activity: DestinyActivityModel = None,
        destiny_class: str = None,
        weapon_type: int = None,
        damage_type: int = None,
    ):
        """Gather all clan members. Return None if something fails"""

        # get the top weapons for the user
        backend_weapons = DestinyWeapons(ctx=None, discord_member=None, discord_guild=guild)
        result = await backend_weapons.get_top(
            discord_id=discord_id,
            input_data=DestinyTopWeaponsInputModel(
                stat=stat,
                weapon_type=weapon_type,
                damage_type=damage_type,
                character_class=destiny_class,
                mode=mode,
                activity_hashes=activity.activity_ids if activity else None,
                start_time=start_time,
                end_time=end_time,
            ),
        )

        results.append(result)


def setup(client):
    command = WeaponsMeta(client)

    # register the autocomplete callback
    command.meta.autocomplete("activity")(autocomplete_send_activity_name)


def meta_subprocess(
    results: list[DestinyTopWeaponsModel],
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    clan_info: DestinyClanModel,
    mode: Optional[int] = None,
    activity: Optional[DestinyActivityModel] = None,
    destiny_class: Optional[str] = None,
    weapon_type: Optional[int] = None,
    damage_type: Optional[int] = None,
) -> Embed:
    """Run in anyio subprocess on another thread since this might be slow"""

    # loop through the results and combine the weapon stats
    limit = 8
    to_sort = {}
    for result in results:
        for entry in result:
            slot_name = entry[0]
            slot_entries: list[DestinyTopWeaponModel] = getattr(result, slot_name)

            if slot_name not in to_sort:
                to_sort.update({slot_name: {}})

            for item in slot_entries:
                if item.weapon_name not in to_sort[slot_name]:
                    to_sort[slot_name].update({item.weapon_name: item})

                # add the stats
                else:
                    to_sort[slot_name][item.weapon_name].stat_value += item.stat_value

    # sort that
    sorted_slot = {}
    for slot_name, data in to_sort:
        sorted_data: list[DestinyTopWeaponModel] = sorted(data, key=lambda weapon: weapon.stat_value, reverse=True)

        sorted_slot.update({slot_name: sorted_data[:limit]})

    # format the message
    embed = embed_message(
        f"{clan_info.name}'s Weapon Meta",
        f"Date: {Timestamp.fromdatetime(start_time).format(style=TimestampStyles.ShortDateTime)} - {Timestamp.fromdatetime(end_time).format(style=TimestampStyles.ShortDateTime)}",
    )
    if weapon_type:
        embed.description += f"\nWeapon Type: {getattr(custom_emojis, DestinyWeaponTypeEnum(weapon_type).name.lower())} {capitalize_string(DestinyWeaponTypeEnum(weapon_type).name)}"
    if damage_type:
        embed.description += f"\nDamage Type: {getattr(custom_emojis, UsableDestinyDamageTypeEnum(damage_type).name.lower())} {capitalize_string(UsableDestinyDamageTypeEnum(damage_type).name)}"

    # set the footer
    footer = []
    if mode:
        footer.append(f"Mode: {capitalize_string(UsableDestinyActivityModeTypeEnum(mode).name)}")
    if activity:
        footer.append(f"Activity: {activity.name}")
    if destiny_class:
        footer.append(f"Class: {getattr(custom_emojis, destiny_class.lower())} {destiny_class}")
    if footer:
        embed.set_footer(" | ".join(footer))

    return embed
