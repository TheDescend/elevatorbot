from prometheus_client import Counter, Gauge, Histogram

BUCKETS = (1, 1.5, 3, 5, 10, 30, 1 * 60, 2 * 60, 5 * 60, 10 * 60, 15 * 60, float("inf"))

prom_cache = Gauge("backend_cache_count", "Amount of objects in internal caches", labelnames=["name"])

prom_registered_users = Gauge("backend_users", "Amount of registered users")

prom_clan_activities = Counter("backend_clan_activity", "How many clan members users play with", labelnames=["user_id"])


endpoint_labels = ["raw_route", "real_route", "guild_id", "user_id"]

prom_endpoints_registered = Gauge("backend_endpoints_registered", "Amount of endpoints")

prom_endpoints_perf = Histogram(
    "backend_endpoints_perf",
    "Amount of calls and the time of execution of the endpoint",
    labelnames=endpoint_labels,
    buckets=BUCKETS,
)
prom_endpoints_running = Gauge(
    "backend_endpoints_running",
    "Amount of concurrently running endpoint callbacks",
    labelnames=endpoint_labels,
)
prom_endpoints_errors = Counter(
    "backend_endpoints_errors",
    "Amount of errors experienced in endpoints",
    labelnames=endpoint_labels,
)

bungie_labels = ["with_token", "route"]

prom_bungie_perf = Histogram(
    "backend_bungie_perf",
    "Amount of api calls and the execution time",
    labelnames=bungie_labels,
    buckets=BUCKETS,
)
prom_bungie_running = Gauge(
    "backend_bungie_running",
    "Amount of api calls currently running",
    labelnames=bungie_labels,
)
prom_bungie_errors = Counter(
    "backend_bungie_errors",
    "Amount of errors experienced from bungie",
    labelnames=bungie_labels,
)
