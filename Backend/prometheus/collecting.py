from sqlalchemy import func, select

from Backend.bungio.manifest import destiny_manifest
from Backend.database import DiscordUsers, acquire_db_session
from Backend.misc.cache import cache
from Backend.prometheus.stats import prom_cache, prom_registered_users


async def collect_prometheus_stats():
    # cache stats
    for k, v in cache.__dict__.items():
        counter = prom_cache.labels(name=k)
        counter.set(len(v))
    for k, v in destiny_manifest.__dict__.items():
        if k.startswith("_"):
            counter = prom_cache.labels(name=k.removeprefix("_"))
            try:
                counter.set(len(v))
            except TypeError:
                pass

    # registered users
    query = select(func.count()).select_from(DiscordUsers).filter(DiscordUsers.token.is_not(None))
    async with acquire_db_session() as db:
        result = await db.execute(query)
        result = result.scalar()
    prom_registered_users.set(result)
