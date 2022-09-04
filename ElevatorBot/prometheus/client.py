from typing import Any

import naff
from naff import BaseCommand, Context, InteractionContext, PrefixedContext

from ElevatorBot.prometheus.stats import (
    interactions_registered_descend,
    interactions_registered_global,
    interactions_sync,
    slash_command_errors,
    slash_commands_perf,
    slash_commands_running,
)
from Shared.functions.readSettingsFile import get_setting


class StatsClient(naff.Client):
    async def synchronise_interactions(self) -> None:
        with interactions_sync.time():
            await super().synchronise_interactions()

        interactions_registered_global.set(len(self.interactions[0]))
        interactions_registered_descend.set(len(self.interactions[get_setting("COMMAND_GUILD_SCOPE")[0]]))

    async def _run_slash_command(self, command: BaseCommand, ctx: Context) -> Any:
        if isinstance(ctx, InteractionContext) and ctx.target_id:
            labels = dict(
                base_name=command.name.default,
                group_name=None,
                command_name=None,
                command_id=command.cmd_id,
            )
        else:
            labels = dict(
                base_name=command.name.default,
                group_name=command.group_name.default,
                command_name=command.sub_cmd_name.default,
                command_id=command.cmd_id,
            )

        if guild := ctx.guild:
            guild_labels = dict(guild_id=guild.id, guild_name=guild.name, dm=0)
        else:
            guild_labels = dict(guild_id=None, guild_name=None, dm=1)

        labels["user_id"] = ctx.author.id
        labels.update(guild_labels)

        perf = slash_commands_perf.labels(**labels)
        running = slash_commands_running.labels(**labels)
        with perf.time(), running.track_inprogress():
            return await super()._run_slash_command(command, ctx)

    async def on_command_error(self, ctx: Context, error: Exception, *args, **kwargs) -> None:
        if not isinstance(ctx, PrefixedContext):
            if isinstance(ctx, InteractionContext) and ctx.target_id:
                labels = dict(
                    base_name=ctx.command.name.default,
                    group_name=None,
                    command_name=None,
                    command_id=ctx.command.cmd_id,
                )
            else:
                labels = dict(
                    base_name=ctx.command.name.default,
                    group_name=ctx.command.group_name.default,
                    command_name=ctx.command.sub_cmd_name.default,
                    command_id=ctx.command.cmd_id,
                )

            if guild := ctx.guild:
                guild_labels = dict(guild_id=guild.id, guild_name=guild.name, dm=0)
            else:
                guild_labels = dict(guild_id=None, guild_name=None, dm=1)

            labels["user_id"] = ctx.author.id
            labels.update(guild_labels)
            count = slash_command_errors.labels(**labels)
            count.inc()
        return await super().on_command_error(ctx, error, *args, **kwargs)
