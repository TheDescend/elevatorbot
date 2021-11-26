import psutil as psutil
from dis_snek.models import (
    InteractionContext,
    Timestamp,
    TimestampStyles,
    slash_command,
)
from psutil._common import bytes2human

from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.descendOnlyIds import descend_channels
from settings import COMMAND_GUILD_SCOPE
from version import __version__


class Metrics(BaseScale):
    @slash_command(name="metrics", description="Shows interesting ElevatorBot metrics", scopes=COMMAND_GUILD_SCOPE)
    async def _metrics(self, ctx: InteractionContext):
        embed = embed_message("ElevatorBot Metrics")

        # version
        embed.add_field(name="Version", value=f"ElevatorBot@{__version__}", inline=True)

        # start time
        start_time = Timestamp.fromdatetime(ctx.bot.start_time)
        embed.add_field(
            name="Start Time",
            value=f"{start_time.format(style=TimestampStyles.ShortDateTime)}\n{start_time.format(style=TimestampStyles.RelativeTime)}",
            inline=True,
        )

        # guilds
        embed.add_field(name="Guilds", value=f"{len(ctx.bot.guilds):,}", inline=False)

        # commands
        global_commands = 0
        descend_commands = 0
        for scope, command in ctx.bot.interactions.items():
            if scope == "0":
                global_commands += 1
            else:
                descend_commands += 1
        embed.add_field(name="Global Commands", value=f"{global_commands:,}", inline=True)
        embed.add_field(name="Descend Commands", value=f"{descend_commands:,}", inline=True)

        # cpu usage
        embed.add_field(
            name="CPU Usage", value=f"{psutil.cpu_count} cores - {round(psutil.cpu_percent() * 100, 2)}%", inline=False
        )

        # ram usage
        memory = psutil.virtual_memory()
        embed.add_field(
            name="RAM Usage",
            value=f"{bytes2human(memory.used)} / {bytes2human(memory.total)} - {round(memory.percent * 100, 2)}%",
            inline=True,
        )

        # command usage
        commands: dict[str, list[int, int]] = {}
        members: dict[str, int] = {}
        with open("/Logs/ElevatorBot/commands.log" "r") as f:
            for line in f.readline():
                data = line.split(":")[1].split("-")

                # get command info from the logs
                name = "Missing"
                descend = False
                for entry in data:
                    if "CommandName" in entry:
                        name = entry.split("'")[1]
                    elif "GuildID" in entry:
                        if name == entry.split("'")[1] == descend_channels.guild.id:
                            descend = True
                    elif "DiscordName" in entry:
                        discord_name = entry.split("'")[1]
                        if discord_name not in members:
                            members.update({discord_name: 0})
                        members[discord_name] += 1

                if name not in commands:
                    commands.update({name: [0, 0]})
                before_list = commands[name]
                before_list[0] += 1
                if descend:
                    before_list[1] += 1
                commands[name] = before_list

        sorted_commands_usage = [
            f"`{k}` - {v[0]:,} Uses ({v[1]:,} Descend)"
            for k, v in sorted(commands.items(), key=lambda item: item[1][0], reverse=True)
        ][:55]
        embed.add_field(name="Top 5 Commands", value="\n".join(sorted_commands_usage), inline=False)

        sorted_commands_usage_descend = [
            f"`{k}` - {v[0]:,} Uses ({v[1]:,} Descend)"
            for k, v in sorted(commands.items(), key=lambda item: item[1], reverse=True)
        ][:5]
        embed.add_field(name="Top 5 Descend Commands", value="\n".join(sorted_commands_usage_descend), inline=True)

        sorted_members = [
            f"{k} - {v} Commands" for k, v in sorted(commands.items(), key=lambda item: item[1][1], reverse=True)
        ][:5]
        embed.add_field(name="Top 5 Members", value="\n".join(sorted_members), inline=True)

        await ctx.send(embeds=embed)


def setup(client):
    Metrics(client)
