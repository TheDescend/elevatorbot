import datetime
from typing import Optional

from anyio import to_thread
from bungio.models import DamageType, DestinyItemSubType
from naff import Embed, Member, OptionTypes, SlashCommandChoice, Timestamp, TimestampStyles, slash_command, slash_option

from ElevatorBot.commandHelpers import autocomplete
from ElevatorBot.commandHelpers.optionTemplates import (
    autocomplete_activity_option,
    autocomplete_weapon_option,
    default_class_option,
    default_damage_type_option,
    default_expansion_option,
    default_mode_option,
    default_season_option,
    default_time_option,
    default_user_option,
    default_weapon_type_option,
)
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import capitalize_string, embed_message, get_emoji_from_rank
from ElevatorBot.misc.helperFunctions import get_emoji_by_name, parse_datetime_options
from ElevatorBot.networking.destiny.weapons import DestinyWeapons
from ElevatorBot.static.emojis import custom_emojis
from Shared.enums.destiny import DestinyWeaponTypeEnum, UsableDestinyActivityModeTypeEnum
from Shared.networkingSchemas.destiny import (
    DestinyActivityModel,
    DestinyTopWeaponModel,
    DestinyTopWeaponsInputModel,
    DestinyTopWeaponsModel,
    DestinyTopWeaponsStatInputModelEnum,
    DestinyWeaponModel,
)


class WeaponsTop(BaseModule):
    """
    Shows your top Destiny 2 weapon ranking

    :option:weapon: If you want a specific weapon to be included in the ranking. Otherwise the command will only show your top eight weapons per slot
    """

    @slash_command(name="weapons_top", description="Shows your top Destiny 2 weapon ranking", dm_permission=False)
    @slash_option(
        name="stat",
        description="Which stat you want the leaderboard to consider. Default: Kills",
        required=False,
        opt_type=OptionTypes.STRING,
        choices=[
            SlashCommandChoice(name="Kills", value="kills"),
            SlashCommandChoice(name="Precision Kills", value="precision_kills"),
        ],
    )
    @autocomplete_weapon_option(description="If you want a specific weapon to be included in the ranking")
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
    @default_user_option()
    async def top_weapons(
        self,
        ctx: ElevatorInteractionContext,
        stat: str = "kills",
        weapon: str = None,
        mode: str = None,
        activity: str = None,
        destiny_class: str = None,
        weapon_type: int = None,
        damage_type: int = None,
        expansion: str = None,
        season: str = None,
        start_time: str = None,
        end_time: str = None,
        user: Member = None,
    ):
        mode = int(mode) if mode else None

        stat = (
            DestinyTopWeaponsStatInputModelEnum.KILLS
            if stat == "kills"
            else DestinyTopWeaponsStatInputModelEnum.PRECISION_KILLS
        )

        # parse start and end time
        start_time, end_time = await parse_datetime_options(
            ctx=ctx, expansion=expansion, season=season, start_time=start_time, end_time=end_time
        )
        if not start_time:
            return

        # get the actual weapon / activities
        if weapon:
            weapon = autocomplete.weapons[weapon.lower()]
        if activity:
            activity = autocomplete.activities[activity.lower()]

        limit = 5 if weapon else 6

        member = user or ctx.author
        backend_weapons = DestinyWeapons(ctx=ctx, discord_member=member, discord_guild=ctx.guild)

        # get the top weapons
        stats = await backend_weapons.get_top(
            input_data=DestinyTopWeaponsInputModel(
                stat=stat,
                how_many_per_slot=limit,
                include_weapon_with_ids=weapon.reference_ids if weapon else None,
                weapon_type=weapon_type,
                damage_type=damage_type,
                character_class=destiny_class,
                mode=mode,
                activity_hashes=activity.activity_ids if activity else None,
                start_time=start_time,
                end_time=end_time,
            )
        )

        # format the message
        embed = await to_thread.run_sync(
            top_subprocess,
            stats,
            stat,
            member,
            limit,
            start_time,
            end_time,
            weapon,
            mode,
            activity,
            destiny_class,
            weapon_type,
            damage_type,
        )

        await ctx.send(embeds=embed)


def setup(client):
    command = WeaponsTop(client)

    # register the autocomplete callback
    command.top_weapons.autocomplete("weapon")(autocomplete.autocomplete_send_weapon_name)
    command.top_weapons.autocomplete("activity")(autocomplete.autocomplete_send_activity_name)


def top_subprocess(
    stats: DestinyTopWeaponsModel,
    stat: DestinyTopWeaponsStatInputModelEnum,
    member: Member,
    limit: int,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    weapon: Optional[DestinyWeaponModel] = None,
    mode: Optional[int] = None,
    activity: Optional[DestinyActivityModel] = None,
    destiny_class: Optional[str] = None,
    weapon_type: Optional[int] = None,
    damage_type: Optional[int] = None,
) -> Embed:
    """Run in anyio subprocess on another thread since this might be slow"""

    if activity:
        mode = None

    embed = embed_message(
        f"Top Weapons",
        f"Date: {Timestamp.fromdatetime(start_time).format(style=TimestampStyles.ShortDateTime)} - {Timestamp.fromdatetime(end_time).format(style=TimestampStyles.ShortDateTime)}",
        member=member,
    )
    if weapon_type:
        embed.description += f"\nWeapon Type: {getattr(custom_emojis, DestinyItemSubType(weapon_type).name.lower(), custom_emojis.question)} {capitalize_string(DestinyWeaponTypeEnum(weapon_type).name)}"
    if damage_type:
        embed.description += f"\nDamage Type: {getattr(custom_emojis, DamageType(damage_type).name.lower(), custom_emojis.question)} {capitalize_string(DamageType(damage_type).name)}"

    # set the footer
    footer = []
    if mode:
        footer.append(f"Mode: {capitalize_string(UsableDestinyActivityModeTypeEnum(mode).name)}")
    if activity:
        footer.append(f"Activity: {activity.name}")
    if destiny_class:
        footer.append(f"Class: {destiny_class}")
    if footer:
        embed.set_footer(" | ".join(footer))

    # add the fields to the embed
    for entry in stats:
        slot_name = entry[0]
        slot_entries: list[DestinyTopWeaponModel] = getattr(stats, slot_name)

        field_text = []
        for item in slot_entries:
            # use the special emojis
            emoji = get_emoji_from_rank(item.ranking)

            # if this is the sought weapon
            if weapon and weapon.reference_ids[0] in item.weapon_ids:
                # append the ... if the sought weapon is in here
                if len(field_text) == limit:
                    field_text.append("...")

                field_text.append(
                    f"""**{emoji} {get_emoji_by_name(DestinyItemSubType, item.weapon_type)}[{item.weapon_name}](https://www.light.gg/db/items/{item.weapon_ids[0]})\n{custom_emojis.enter} {capitalize_string(stat.name)}: {item.stat_value:,}**"""
                )

            # if it is not the sought weapon
            else:
                if len(field_text) < limit:
                    field_text.append(
                        f"""{emoji} {get_emoji_by_name(DestinyItemSubType, item.weapon_type)}[{item.weapon_name}](https://www.light.gg/db/items/{item.weapon_ids[0]})\n{custom_emojis.enter} {capitalize_string(stat.name)}: {item.stat_value:,}"""
                    )

        if field_text:
            embed.add_field(name=slot_name.capitalize(), value="\n".join(field_text), inline=True)

    return embed
