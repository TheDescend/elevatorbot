from dis_snek.models import InteractionContext, Member, slash_command

from DestinyEnums.enums import UsableDestinyActivityModeTypeEnum
from ElevatorBot.backendNetworking.destiny.activities import DestinyActivities
from ElevatorBot.commandHelpers.autocomplete import activities, activities_by_id
from ElevatorBot.commandHelpers.optionTemplates import (
    autocomplete_activity_option,
    default_class_option,
    default_mode_option,
    default_user_option,
)
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message, format_timedelta
from ElevatorBot.static.emojis import custom_emojis


class Last(BaseScale):
    @slash_command(name="last", description="Stats for the last activity you played")
    @default_mode_option(description="Restrict the game mode. Default: All modes")
    @autocomplete_activity_option(description="Restrict the activity. Overwrite `mode`. Default: All modes")
    @default_class_option(description="Restrict the class. Default: All classes")
    @default_user_option()
    async def _last(
        self,
        ctx: InteractionContext,
        mode: str = None,
        activity: str = None,
        destiny_class: str = None,
        user: Member = None,
    ):
        mode = int(mode) if mode else None

        # might take a sec
        await ctx.defer()

        # get the activity ids
        activity_ids = None
        if activity:
            activity_data = activities[activity.lower()]
            activity_ids = activity_data.activity_ids

        member = user or ctx.author
        db_activities = DestinyActivities(ctx=ctx, client=ctx.bot, discord_guild=ctx.guild, discord_member=member)

        result = await db_activities.last(
            activity_ids=activity_ids,  # if this is supplied, mode is ignored
            mode=UsableDestinyActivityModeTypeEnum(mode) if mode else UsableDestinyActivityModeTypeEnum.ALL,
            character_class=destiny_class,
        )
        if not result:
            return

        # prepare embed
        embed = embed_message(
            f"{member.display_name}'s Last Activity",
            f"""**{activities_by_id[result.reference_id]}{(' - ' + str(result.score) + ' Points') if result.score > 0 else ""} - {format_timedelta(result.activity_duration_seconds)}**""",
            f"""InstanceID: {result.instance_id}""",
        )
        embed.timestamp = result.period

        # set footer
        footer = []
        if destiny_class:
            footer.append(f"Class: {getattr(custom_emojis, destiny_class.lower())} {destiny_class}")
        if mode:
            footer.append(
                f"""Mode: {" ".join(
                [part.capitalize().replace("Pve", "PvE").replace("Pvp", "PvP") for part in UsableDestinyActivityModeTypeEnum(mode).name.split["_"]]
            )}"""
            )
        if activity:
            footer.append(f"Activity: {activity}")
        if footer:
            embed.set_footer(" | ".join(footer))

        class_emojis = {"Warlock": custom_emojis.warlock, "Hunter": custom_emojis.hunter, "Titan": custom_emojis.titan}
        for player in result.users:
            # sometimes people dont have a class for some reason. Skipping that
            if player.character_class == "":
                continue

            player_data = [
                f"""K: **{player.kills}**, D: **{player.deaths}**, A: **{player.assists}**""",
                f"""K/D: **{round((player.kills / player.deaths) if player.deaths > 0 else player.kills, 2)}** {"(DNF)" if not player.completed else ""}""",
                format_timedelta(player.time_played_seconds),
            ]

            embed.add_field(
                name=f"""{getattr(custom_emojis, player.character_class)} {player.bungie_name} {custom_emojis.light_level_icon} {player.light_level}""",
                value="\n".join(player_data),
                inline=True,
            )

        await ctx.send(embeds=embed)


def setup(client):
    Last(client)
