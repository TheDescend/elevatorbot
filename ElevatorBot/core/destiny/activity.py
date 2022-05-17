import datetime

from naff import Member, Timestamp, TimestampStyles

from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import add_filler_field, embed_message, format_timedelta
from Shared.networkingSchemas import DestinyActivityOutputModel


async def format_and_send_activity_data(
    ctx: ElevatorInteractionContext,
    member: Member,
    stats: DestinyActivityOutputModel,
    name: str,
    activity_name: str,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    destiny_class: str | None = None,
):
    """Formats and sends data for the /activity and /mode command"""

    # make the data pretty
    description = [
        f"Name: {activity_name}",
        f"Date: {Timestamp.fromdatetime(start_time).format(style=TimestampStyles.ShortDateTime)} - "
        f"{Timestamp.fromdatetime(end_time).format(style=TimestampStyles.ShortDateTime)}",
    ]

    embed = embed_message(name, "\n".join(description), member=member)

    # set the footer
    footer = []
    if destiny_class:
        footer.append(f"Class: {destiny_class}")
    if footer:
        embed.set_footer(" | ".join(footer))

    # add the fields
    embed.add_field(name="Full Completions", value=f"{stats.full_completions:,}", inline=True)
    embed.add_field(name="CP Completions", value=f"{stats.cp_completions:,}", inline=True)
    add_filler_field(embed)

    if stats.fastest:
        embed.add_field(name="Time Played", value=format_timedelta(stats.time_spend.seconds), inline=True)
        embed.add_field(name="Average Time", value=format_timedelta(stats.average.seconds), inline=True)
        embed.add_field(
            name="Fastest Time",
            value=f"[{format_timedelta(stats.fastest.seconds)}](https://www.bungie.net/en/PGCR/{stats.fastest_instance_id})",
            inline=True,
        )

    percent = (stats.precision_kills / stats.kills) * 100 if stats.kills else 0
    embed.add_field(name="Kills", value=f"{stats.kills:,} _({round(percent, 2)}% prec)_", inline=True)
    embed.add_field(name="Assists", value=f"{stats.assists:,}", inline=True)
    embed.add_field(name="Deaths", value=f"{stats.deaths:,}", inline=True)

    await ctx.send(embeds=embed)
