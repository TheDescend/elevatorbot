import asyncio
import datetime
import inspect
import logging
import socket
from typing import List, Optional, Sequence

import naff
import prometheus_client
import uvicorn

from ElevatorBot.prometheus.stats import (
    bot_info,
    cache_gauge,
    cache_limits_hard,
    cache_limits_soft,
    channels_gauge,
    descend_voice_channel_activity,
    elevator_version_info,
    guilds_gauge,
    latency_gauge,
    lib_info,
    members_gauge,
    messages_counter,
    start_time_info,
)
from ElevatorBot.static.descendOnlyIds import descend_channels
from Shared.functions.helperFunctions import get_now_with_tz
from version import __version__

logger = logging.getLogger("nafftrack")


users_in_vs: dict[int, datetime.datetime] = {}
vc_lock = asyncio.Lock()


class StatsServer(uvicorn.Server):
    async def serve(self, sockets: Optional[List[socket.socket]] = None) -> None:
        config = self.config
        if not config.loaded:
            config.load()

        self.lifespan = config.lifespan_class(config)
        self.force_exit = True  # to disable waiting for ctrl+c on exit in some cases

        logger.info("Started metrics endpoint server")

        await self.startup(sockets=sockets)
        if self.should_exit:
            return
        try:
            await self.main_loop()
            # set self.should_exit = True to force main loop to exit. Maybe use in some events?
        finally:
            await self.shutdown(sockets=sockets)
            logger.info("Finished metrics endpoint server")

    def _log_started_message(self, listeners: Sequence[socket.SocketType]) -> None:
        config = self.config

        addr_format = "%s://%s:%d"
        host = "0.0.0.0" if config.host is None else config.host
        if ":" in host:
            # It's an IPv6 address.
            addr_format = "%s://[%s]:%d"

        port = config.port
        if port == 0:
            port = listeners[0].getsockname()[1]

        protocol_name = "https" if config.ssl else "http"
        message = f"Uvicorn is running metrics endpoint on {addr_format}"
        logger.info(
            message,
            protocol_name,
            host,
            port,
        )


class Stats(naff.Extension):
    host = "0.0.0.0"
    port = 8877
    interval = 5

    def __init__(self, bot):
        self.server: Optional[StatsServer] = None

        self.bot_caches = {
            name.removesuffix("_cache"): cache
            for name, cache in inspect.getmembers(self.bot.cache, predicate=lambda x: isinstance(x, dict))
            if not name.startswith("__")
        }

    @naff.listen()
    async def on_startup(self) -> None:
        app = prometheus_client.make_asgi_app()
        cfg = uvicorn.Config(app=app, host=self.host, port=self.port, access_log=False)
        self.server = StatsServer(cfg)

        loop = asyncio.get_running_loop()
        loop.create_task(self.server.serve())

        lib_info.info({"version": naff.const.__version__})

        elevator_version_info.info({"version": __version__})

        start_time_info.info({"datetime": f"{self.bot.start_time:%d.%m.%Y, %H:%M} UTC"})

        guilds_gauge.set(len(self.bot.user._guild_ids))

        stats_task = naff.Task(self.collect_stats, naff.triggers.IntervalTrigger(seconds=self.interval))
        stats_task.start()

    @naff.listen()
    async def on_ready(self) -> None:
        bot_info.info(
            {
                "username": self.bot.user.username,
                "discriminator": self.bot.user.discriminator,
                "tag": str(self.bot.user.tag),
            }
        )
        for guild in self.bot.guilds:
            c_gauge = channels_gauge.labels(guild_id=guild.id, guild_name=guild.name)
            m_gauge = members_gauge.labels(guild_id=guild.id, guild_name=guild.name)

            c_gauge.set(len(guild._channel_ids))
            if naff.Intents.GUILD_MEMBERS in self.bot.intents:
                m_gauge.set(len(guild._member_ids))
            else:
                m_gauge.set(guild.member_count)

    @naff.listen()
    async def on_message_create(self, event: naff.events.MessageCreate):
        if guild := event.message.guild:
            counter = messages_counter.labels(
                guild_id=guild.id, guild_name=guild.name, dm=0, user_id=event.message.author.id
            )
        else:
            counter = messages_counter.labels(guild_id=None, guild_name=None, dm=1, user_id=event.message.author.id)

        counter.inc()

    @naff.listen()
    async def on_voice_state_update(self, event: naff.events.VoiceStateUpdate):
        if event.guild != descend_channels.guild:
            return

        async with vc_lock:
            # user was in vc before
            if event.before:
                user_id = event.before.member.id
                if user_id in users_in_vs:
                    join_date = users_in_vs.pop(user_id)
                    metric = descend_voice_channel_activity.labels(channel_id=event.before.channel.id, user_id=user_id)
                    metric.observe((get_now_with_tz() - join_date).seconds)

            # save user join time
            if event.after:
                user_id = event.after.member.id
                users_in_vs[user_id] = get_now_with_tz()

    async def collect_stats(self):
        # Latency stats
        if latency := self.bot.ws.latency:
            latency_gauge.set(latency[-1])

        # Cache stats
        for name, cache in self.bot_caches.items():
            cache_g = cache_gauge.labels(name=name)
            cache_limits_soft_g = cache_limits_soft.labels(name=name)
            cache_limits_hard_g = cache_limits_hard.labels(name=name)

            cache_g.set(len(cache))
            if isinstance(cache, naff.smart_cache.TTLCache):
                cache_limits_soft_g.set(cache.soft_limit)
                cache_limits_hard_g.set(cache.hard_limit)
            else:
                cache_limits_soft_g.set("inf")
                cache_limits_hard_g.set("inf")

    @naff.listen()
    async def on_guild_join(self, _):
        # ignore guild_join events during bot initialization
        if not self.bot.is_ready:
            return

        guilds_gauge.inc()

    @naff.listen()
    async def on_guild_left(self, _):
        guilds_gauge.dec()

    @naff.listen()
    async def on_member_remove(self, event: naff.events.MemberRemove):
        gauge = members_gauge.labels(guild_id=event.guild.id, guild_name=event.guild.name)
        gauge.dec()

    @naff.listen()
    async def on_member_add(self, event: naff.events.MemberAdd):
        gauge = members_gauge.labels(guild_id=event.guild.id, guild_name=event.guild.name)
        gauge.inc()

    @naff.listen()
    async def on_channel_delete(self, event: naff.events.ChannelDelete):
        gauge = channels_gauge.labels(guild_id=event.channel.guild.id, guild_name=event.channel.guild.name)
        gauge.dec()

    @naff.listen()
    async def on_channel_create(self, event: naff.events.ChannelCreate):
        gauge = channels_gauge.labels(guild_id=event.channel.guild.id, guild_name=event.channel.guild.name)
        gauge.inc()

    # @naff.listen()
    # async def on_guild_unavailable(self, event):
    #     guilds_gauge.set(len(self.bot.user._guild_ids))


def setup(client):
    Stats(client)
