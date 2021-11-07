from dis_snek.models import (
    InteractionContext,
    Member,
    Timestamp,
    TimestampStyles,
    slash_command,
)

from ElevatorBot.backendNetworking.destiny.activities import DestinyActivities
from ElevatorBot.commandHelpers.autocomplete import activities
from ElevatorBot.commandHelpers.optionTemplates import (
    autocomplete_activity_option,
    default_class_option,
    default_expansion_option,
    default_season_option,
    default_time_option,
    default_user_option,
)
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message, format_timedelta
from ElevatorBot.misc.helperFunctions import parse_datetime_options
from ElevatorBot.static.emojis import custom_emojis
from NetworkingSchemas.destiny.activities import DestinyActivityInputModel


class DestinyActivity(BaseScale):
    @slash_command(name="activity", description="Display stats for the chosen activity")
    @autocomplete_activity_option(description="Chose the activity you want to see the stats for", required=True)
    @default_class_option(description="Restrict the class where the weapon stats count. Default: All classes")
    @default_expansion_option(description="Restrict the expansion where the weapon stats count")
    @default_season_option(description="Restrict the season where the weapon stats count")
    @default_time_option(
        name="start_time",
        description="Format: `HH:MM DD/MM` - Input the **earliest** date you want the weapon stats for. Default: Jesus's Birth",
    )
    @default_time_option(
        name="end_time",
        description="Format: `HH:MM DD/MM` - Input the **latest** date you want the weapon stats for. Default: Now",
    )
    @default_user_option()
    async def _activity(
        self,
        ctx: InteractionContext,
        activity: str,
        destiny_class: str = None,
        expansion: str = None,
        season: str = None,
        start_time: str = None,
        end_time: str = None,
        user: Member = None,
    ):
        # parse start and end time
        start_time, end_time = parse_datetime_options(
            ctx=ctx, expansion=expansion, season=season, start_time=start_time, end_time=end_time
        )
        if not start_time:
            return

        # get the actual activity
        if activity:
            activity = activities[activity.lower()]

        # might take a sec
        await ctx.defer()

        member = user or ctx.author
        backend_activities = DestinyActivities(ctx=ctx, client=ctx.bot, discord_member=member, discord_guild=ctx.guild)

        # get the stats
        stats = await backend_activities.get_activity_stats(
            input_model=DestinyActivityInputModel(
                activity_ids=activity.activity_ids,
                character_class=destiny_class,
                start_time=start_time,
                end_time=end_time,
            )
        )
        if not stats:
            return

        # make the data pretty
        description = [
            f"Name: {activity.name}",
            f"Date: {Timestamp.fromdatetime(start_time).format(style=TimestampStyles.ShortDateTime)} - {Timestamp.fromdatetime(end_time).format(style=TimestampStyles.ShortDateTime)}",
        ]

        embed = embed_message(f"{member.display_name}'s Activity Stats", "\n".join(description))

        # set the footer
        footer = []
        if destiny_class:
            footer.append(f"Class: {getattr(custom_emojis, destiny_class.lower())} {destiny_class}")
        if footer:
            embed.set_footer(" | ".join(footer))

        # add the fields
        embed.add_field(name="Full Completions", value=str(stats.full_completions), inline=True)
        embed.add_field(name="CP Completions", value=str(stats.cp_completions), inline=True)
        if stats.fastest:
            embed.add_field(name="Time Played", value=format_timedelta(stats.time_spend.seconds), inline=False)
            embed.add_field(name="Average Time", value=format_timedelta(stats.average.seconds), inline=True)
            embed.add_field(
                name="Fastest Time",
                value=f"[{format_timedelta(stats.fastest.seconds)}[(https://www.bungie.net/en/PGCR/{stats.fastest_instance_id})",
                inline=True,
            )
        embed.add_field(
            name="Kills", value=f"{stats.kills} _({(stats.precision_kills / stats.kills) * 100}% prec)_", inline=False
        )
        embed.add_field(name="Assists", value=str(stats.assists), inline=True)
        embed.add_field(name="Deaths", value=str(stats.deaths), inline=True)

        await ctx.send(embeds=embed)


def setup(client):
    DestinyActivity(client)
