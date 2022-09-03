import logging
import os

import naff

import nafftrack

logging.basicConfig(level=logging.INFO)

debug = bool(int(os.environ.get("DEBUG", "0").strip()))
debug_scope = os.environ.get("DEBUG_SCOPE", naff.MISSING)
debug_scope = debug_scope.strip() if debug_scope else debug_scope

client = nafftrack.client.StatsClient(
    asyncio_debug=debug,
    sync_interactions=True,
    debug_scope=debug_scope,
)

client.load_extension("naff.ext.debug_extension")
client.load_extension("nafftrack.extension")

client.start(os.environ["DISCORD_TOKEN"].strip())
