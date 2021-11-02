from typing import Optional

from dis_snek.models import InteractionContext, Member

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.misc.helperFunctions import get_character_ids_from_class
from ElevatorBot.static.destinyEnums import StatScope

stat_translation = {
    "Kills": "kills",
    "Precision Kills": "precisionKills",
    "Assists": "assists",
    "Deaths": "deaths",
    "Suicides": "suicides",
    "KDA": "efficiency",
    "Longest Kill Distance": "longestKillDistance",
    "Average Kill Distance": "averageKillDistance",
    "Total Kill Distance": "totalKillDistance",
    "Longest Kill Spree": "longestKillSpree",
    "Average Lifespan": "averageLifespan",
    "Resurrections Given": "resurrectionsPerformed",
    "Resurrections Received": "resurrectionsReceived",
    "Number of Players Played With": "allParticipantsCount",
    "Longest Single Life (in seconds)": "longestSingleLife",
    "Orbs of Power Dropped": "orbsDropped",
    "Orbs of Power Gathered": "orbsGathered",
    "Time Played (in seconds)": "secondsPlayed",
    "Activities Cleared": "activitiesCleared",
    "Public Events Completed": "publicEventsCompleted",
    "Heroic Public Events Completed": "heroicPublicEventsCompleted",
    "Kills with: Super": "weaponKillsSuper",
    "Kills with: Melee": "weaponKillsMelee",
    "Kills with: Grenade": "weaponKillsGrenade",
    "Kills with: Ability": "weaponKillsAbility",
}


async def get_stat_and_send(
    ctx: InteractionContext,
    stat_vanity_name: str,
    stat_bungie_name: str,
    scope: StatScope,
    member: Member,
    destiny_class: Optional[str] = None,
):
    """Gets the stat specified in the context and sends the message"""

    # might take a sec
    await ctx.defer()

    account = DestinyAccount(discord_guild=ctx.guild, discord_member=member, client=ctx.bot)

    # check if we need a user stat or a char stat
    if destiny_class:
        # get the users characters
        character_ids = await get_character_ids_from_class(ctx=ctx, profile=account, destiny_class=destiny_class)
        if not character_ids:
            return

        # get the stats for each character ID
        stat_value = -1
        for character_id in character_ids:
            result = await account.get_stat_by_characters(
                character_id=character_id, stat_name=stat_bungie_name, stat_category=scope.value
            )

            # catch errors
            if not result:
                await result.send_error_message(ctx=ctx)
                return

            # handle the stat calc differently depending on what stat it is
            if stat_bungie_name in ["efficiency", "averageKillDistance", "averageLifespan"]:
                # take the average
                if stat_value is -1:
                    stat_value = result.result["value"]
                else:
                    stat_value = (stat_value + result.result["value"]) / 2

            elif stat_bungie_name in ["longestKillDistance", "longestKillSpree", "longestSingleLife"]:
                # take the highest
                if stat_value is -1:
                    stat_value = result.result["value"]
                else:
                    if result.result["value"] > stat_value:
                        stat_value = result.result["value"]

            else:
                # add them together
                if stat_value is -1:
                    stat_value = result.result["value"]
                else:
                    if result.result["value"] > stat_value:
                        stat_value = stat_value + result.result["value"]

    else:
        # get stats for the user
        result = await account.get_stat(stat_name=stat_bungie_name, stat_category=scope.value)

        # catch errors
        if not result:
            await result.send_error_message(ctx=ctx)
            return

        stat_value = result.result["value"]

    # format and send the stat message
    await ctx.send(
        embeds=embed_message(
            f"{member.display_name}'s Stat Info",
            f"Your `{stat_vanity_name}` stat is currently at **{stat_value:,}**",
        )
    )