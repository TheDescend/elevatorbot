from dis_snek.models import (
    InteractionContext,
    Member,
    Timestamp,
    TimestampStyles,
    slash_command,
)

from DestinyEnums.enums import (
    DestinyWeaponTypeEnum,
    UsableDestinyActivityModeTypeEnum,
    UsableDestinyAmmunitionTypeEnum,
    UsableDestinyDamageTypeEnum,
)
from ElevatorBot.backendNetworking.destiny.weapons import DestinyWeapons
from ElevatorBot.commandHelpers.autocomplete import (
    activities,
    autocomplete_send_activity_name,
    autocomplete_send_weapon_name,
    weapons,
)
from ElevatorBot.commandHelpers.optionTemplates import (
    autocomplete_activity_option,
    autocomplete_weapon_option,
    default_class_option,
    default_expansion_option,
    default_mode_option,
    default_season_option,
    default_time_option,
    default_user_option,
)
from ElevatorBot.commandHelpers.subCommandTemplates import weapons_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import capitalize_string, embed_message
from ElevatorBot.misc.helperFunctions import parse_datetime_options
from ElevatorBot.static.emojis import custom_emojis
from NetworkingSchemas.destiny.weapons import DestinyWeaponStatsInputModel


class WeaponsWeapon(BaseScale):
    @slash_command(
        **weapons_sub_command,
        sub_cmd_name="weapon",
        sub_cmd_description="Shows Destiny 2 weapon stats for the specified weapon",
    )
    @autocomplete_weapon_option(description="The weapon you want to look up", required=True)
    @default_mode_option()
    @autocomplete_activity_option()
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
    async def weapon(
        self,
        ctx: InteractionContext,
        weapon: str,
        mode: str = None,
        activity: str = None,
        destiny_class: str = None,
        expansion: str = None,
        season: str = None,
        start_time: str = None,
        end_time: str = None,
        user: Member = None,
    ):
        mode = int(mode) if mode else None

        # parse start and end time
        start_time, end_time = await parse_datetime_options(
            ctx=ctx, expansion=expansion, season=season, start_time=start_time, end_time=end_time
        )
        if not start_time:
            return

        # get the actual weapon / activity
        weapon = weapons[weapon.lower()]
        if activity:
            activity = activities[activity.lower()]

        member = user or ctx.author
        backend_weapons = DestinyWeapons(ctx=ctx, discord_member=member, discord_guild=ctx.guild)

        # get the stats
        stats = await backend_weapons.get_weapon(
            input_data=DestinyWeaponStatsInputModel(
                weapon_ids=weapon.reference_ids,
                character_class=destiny_class,
                mode=mode,
                activity_hashes=activity.activity_ids if activity else None,
                start_time=start_time,
                end_time=end_time,
            )
        )

        # format them nicely
        description = [
            f"Weapon: [{weapon.name}](https://www.light.gg/db/items/{weapon.reference_ids[0]})",
            f"""Weapon Type: {getattr(custom_emojis, getattr(DestinyWeaponTypeEnum, "_".join(weapon.weapon_type.upper().split())).name.lower())} {weapon.weapon_type}""",
            f"""Damage Type: {getattr(custom_emojis, getattr(UsableDestinyDamageTypeEnum, "_".join(weapon.damage_type.upper().split())).name.lower())} {weapon.damage_type}""",
            f"""Ammo Type: {getattr(custom_emojis, getattr(UsableDestinyAmmunitionTypeEnum, "_".join(weapon.ammo_type.upper().split())).name.lower())} {weapon.ammo_type}""",
            "⁣",
            f"Date: {Timestamp.fromdatetime(start_time).format(style=TimestampStyles.ShortDateTime)} - {Timestamp.fromdatetime(end_time).format(style=TimestampStyles.ShortDateTime)}",
        ]
        embed = embed_message(f"{member.display_name}'s Weapon Stats", "\n".join(description))

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

        # add the fields
        embed.add_field(name="Total Kills", value=f"**{custom_emojis.enter} {stats.total_kills:,}**", inline=True)
        embed.add_field(
            name="Total Precision Kills",
            value=f"{custom_emojis.enter} **{stats.total_precision_kills:,}**",
            inline=True,
        )
        percent = (stats.total_precision_kills / stats.total_kills) * 100 if stats.total_kills else 0
        embed.add_field(
            name="% Precision Kills",
            value=f"{custom_emojis.enter} **{round(percent, 2)}%**",
            inline=True,
        )
        embed.add_field(
            name="Average Kills",
            value=f"{custom_emojis.enter} **{round((stats.total_kills / stats.total_activities), 2)}**\nIn `{stats.total_activities}` activities",
            inline=True,
        )
        embed.add_field(
            name="Maximum Kills",
            value=f"{custom_emojis.enter} **{stats.best_kills:,}**\n[View Activity Details](https://www.bungie.net/en/PGCR/{stats.best_kills_activity_id})\n{stats.best_kills_activity_name}\nDate: {Timestamp.fromdatetime(stats.best_kills_date).format(style=TimestampStyles.ShortDateTime)}",
            inline=True,
        )
        await ctx.send(embeds=embed)


def setup(client):
    command = WeaponsWeapon(client)

    # register the autocomplete callback
    command.weapon.autocomplete("weapon")(autocomplete_send_weapon_name)
    command.weapon.autocomplete("activity")(autocomplete_send_activity_name)
