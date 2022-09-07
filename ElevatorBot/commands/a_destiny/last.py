from naff import Member, Timestamp, TimestampStyles, slash_command

from ElevatorBot.commandHelpers import autocomplete
from ElevatorBot.commandHelpers.optionTemplates import (
    autocomplete_activity_option,
    default_class_option,
    default_mode_option,
    default_user_option,
)
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import capitalize_string, embed_message, format_timedelta
from ElevatorBot.networking.destiny.activities import DestinyActivities
from ElevatorBot.static.emojis import custom_emojis
from Shared.enums.destiny import UsableDestinyActivityModeTypeEnum


class Last(BaseModule):
    @slash_command(name="last", description="Stats for the last Destiny 2 activity you played", dm_permission=False)
    @default_mode_option()
    @autocomplete_activity_option()
    @default_class_option()
    @default_user_option()
    async def last(
        self,
        ctx: ElevatorInteractionContext,
        mode: str = None,
        activity: str = None,
        destiny_class: str = None,
        user: Member = None,
    ):
        mode = int(mode) if mode else None

        # get the activity ids
        if activity:
            mode = None
            activity = autocomplete.activities[activity.lower()]

        member = user or ctx.author
        db_activities = DestinyActivities(ctx=ctx, discord_guild=ctx.guild, discord_member=member)

        result = await db_activities.last(
            activity_ids=activity.activity_ids if activity else None,  # if this is supplied, mode is ignored
            mode=UsableDestinyActivityModeTypeEnum(mode) if mode else UsableDestinyActivityModeTypeEnum.ALL,
            character_class=destiny_class,
        )

        # prepare embed
        embed = embed_message(
            "Last Activity",
            f"""**{autocomplete.activities_by_id[result.reference_id].name}{(' - ' + str(result.score) + ' Points') if result.score > 0 else ""} - {Timestamp.fromdatetime(result.period).format(style=TimestampStyles.ShortDateTime)} - [{format_timedelta(result.activity_duration_seconds)}](https://www.bungie.net/en/PGCR/{result.instance_id})**""",
            member=member,
        )

        # set footer
        footer = []
        if destiny_class:
            footer.append(f"Class: {destiny_class}")
        if mode:
            footer.append(f"Mode: {capitalize_string(UsableDestinyActivityModeTypeEnum(mode).name)}")
        if activity:
            footer.append(f"Activity: {activity.name}")
        if footer:
            embed.set_footer(" | ".join(footer))

        for player in result.users:
            # sometimes people don't have a class for some reason. Skipping that
            if player.character_class == "":
                continue

            # get the discord user
            discord_user = (
                ctx.bot.cache.get_member(guild_id=ctx.guild.id, user_id=player.discord_id)
                if player.discord_id
                else None
            )

            player_data = [
                f"**{getattr(custom_emojis, player.character_class.lower(), custom_emojis.question)} {player.bungie_name if not discord_user else discord_user.mention}**",
                f"{custom_emojis.light_level} {player.light_level}",
                "⁣",
                f"K: **{player.kills}**, D: **{player.deaths}**, A: **{player.assists}**",
                f"""K/D: **{round((player.kills / player.deaths) if player.deaths > 0 else player.kills, 2)}** {"(DNF)" if not player.completed else ""}""",
                format_timedelta(player.time_played_seconds),
            ]

            embed.add_field(
                name="⁣",
                value="\n".join(player_data),
                inline=True,
            )

        await ctx.send(embeds=embed)


def setup(client):
    command = Last(client)

    # register the autocomplete callback
    command.last.autocomplete("activity")(autocomplete.autocomplete_send_activity_name)
