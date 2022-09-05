from prometheus_client import Counter, Gauge, Histogram, Info, Summary

BUCKETS = (1, 1.5, 3, 5, 10, 30, 1 * 60, 2 * 60, 5 * 60, 10 * 60, 15 * 60, float("inf"))
slash_labels = [
    "base_name",
    "group_name",
    "command_name",
    "command_id",
    "guild_id",
    "guild_name",
    "dm",
    "user_id",
]

# nafftrack stats
lib_info = Info("naff", "Basic info about naff library")
bot_info = Info("naff_bot", "Basic attributes of the running bot")
latency_gauge = Gauge("naff_bot_latency", "Latency of the websocket connection")

cache_gauge = Gauge("naff_cache_count", "Amount of objects in internal caches", labelnames=["name"])
cache_limits_soft = Gauge("naff_cache_soft_limits", "Soft limits on the caches", labelnames=["name"])
cache_limits_hard = Gauge("naff_cache_hard_limits", "Hard limits on the caches", labelnames=["name"])


messages_counter = Counter(
    "naff_received_messages",
    "Amount of received messages",
    labelnames=["guild_id", "guild_name", "channel_id", "channel_name", "dm", "user_id"],
)

guilds_gauge = Gauge("naff_guilds", "Amount of guilds this bot is in")
channels_gauge = Gauge("naff_channels", "Amount of channels this bot is in", labelnames=["guild_id", "guild_name"])
members_gauge = Gauge("naff_members", "Amount of members this bot can see", labelnames=["guild_id", "guild_name"])

interactions_sync = Summary("naff_interactions_sync", "Amount of syncs and time spent syncing interactions")

slash_commands_perf = Histogram(
    "naff_slash_command_perf",
    "Amount of calls and the time of execution of the command",
    labelnames=slash_labels,
    buckets=BUCKETS,
)

slash_commands_running = Gauge(
    "naff_slash_command_running",
    "Amount of concurrently running slash command callbacks",
    labelnames=slash_labels,
)

slash_command_errors = Counter(
    "naff_slash_command_errors",
    "Amount of errors experienced in the bot",
    labelnames=slash_labels,
)

# own stats
elevator_version_info = Info("elevator_version", "Version of Elevator")

start_time_info = Info("naff_bot_start_time", "Start Time")

interactions_registered_global = Gauge(
    "naff_global_interactions_registered", "Amount of globally registered application commands"
)
interactions_registered_descend = Gauge(
    "naff_descend_interactions_registered", "Amount of descend only registered application commands"
)

descend_voice_channel_activity = Histogram(
    "naff_descend_voice_channel_activity",
    "How long users are in voice channels",
    labelnames=["channel_id", "channel_name", "user_id"],
    buckets=BUCKETS,
)
