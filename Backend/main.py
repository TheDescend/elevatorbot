import importlib.util
import logging
import os
import time

import bungio.error as bungio_errors
from fastapi import Depends, FastAPI, Request
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.text import Text
from starlette.responses import Response

from Backend.backgroundEvents import scheduler
from Backend.bungio.client import get_bungio_client
from Backend.bungio.manifest import destiny_manifest
from Backend.core.errors import CustomException, handle_bungio_exception, handle_custom_exception
from Backend.crud import backend_user
from Backend.database.base import acquire_db_session
from Backend.database.models import BackendUser
from Backend.dependencies import auth_get_user_with_read_perm, auth_get_user_with_write_perm
from Backend.prometheus.collecting import collect_prometheus_stats
from Backend.prometheus.stats import (
    prom_endpoints_errors,
    prom_endpoints_perf,
    prom_endpoints_registered,
    prom_endpoints_running,
)
from Backend.startup.initBackgroundEvents import register_background_events
from Backend.startup.initLogging import init_logging
from Shared.functions.logging import DESCEND_COLOUR
from Shared.functions.readSettingsFile import get_setting
from Shared.networkingSchemas.misc.auth import BackendUserModel

# print ascii art
console = Console()
text = Text.assemble(
    (
        """
 ███████ ██      ███████ ██    ██  █████  ████████  ██████  ██████      ██████   █████   ██████ ██   ██ ███████ ███    ██ ██████
 ██      ██      ██      ██    ██ ██   ██    ██    ██    ██ ██   ██     ██   ██ ██   ██ ██      ██  ██  ██      ████   ██ ██   ██
 █████   ██      █████   ██    ██ ███████    ██    ██    ██ ██████      ██████  ███████ ██      █████   █████   ██ ██  ██ ██   ██
 ██      ██      ██       ██  ██  ██   ██    ██    ██    ██ ██   ██     ██   ██ ██   ██ ██      ██  ██  ██      ██  ██ ██ ██   ██
 ███████ ███████ ███████   ████   ██   ██    ██     ██████  ██   ██     ██████  ██   ██  ██████ ██   ██ ███████ ██   ████ ██████
══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
        """,
        DESCEND_COLOUR,
    )
)
console.print(Panel.fit(text, padding=(0, 6), border_style="black"))


# loading bar
startup_progress = Progress()
startup_progress.start()
startup_task = startup_progress.add_task("Starting Up...", total=7)

app = FastAPI()

# init logging
init_logging()

default_logger = logging.getLogger("requests")

try:
    # install uvloop for faster asyncio (docker only)
    import uvloop
except ModuleNotFoundError:
    default_logger.debug("Uvloop not installed, skipping")
else:
    default_logger.debug("Installing uvloop...")
    uvloop.install()
startup_progress.update(startup_task, advance=1)


# healthcheck to see if this is running fine
@app.get("/health_check")
async def health_check():
    return {"status": "alive"}


# only allow people with read permissions
@app.get("/read_perm", response_model=BackendUserModel)
async def read_perm(user: BackendUser = Depends(auth_get_user_with_read_perm)):
    return BackendUserModel.from_orm(user)


# only allow people with write permissions
@app.get("/write_perm", response_model=BackendUserModel)
async def write_perm(user: BackendUser = Depends(auth_get_user_with_write_perm)):
    return BackendUserModel.from_orm(user)


# serve prometheus
@app.get("/metrics")
def metrics(request: Request):
    resp = Response(content=generate_latest(REGISTRY))
    resp.headers["Content-Type"] = CONTENT_TYPE_LATEST

    return resp


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware which logs every request"""

    # calculate the time needed to handle the request
    start_time = time.time()

    # prometheus logging
    query_params = request.query_params
    labels = {
        "raw_route": request.base_url,
        "real_route": request.url,
        "guild_id": query_params.get("guild_id", None),
        "user_id": query_params.get("discord_id", None),
    }
    perf = prom_endpoints_perf.labels(**labels)
    running = prom_endpoints_running.labels(**labels)

    try:
        with perf.time(), running.track_inprogress():
            response = await call_next(request)
    except Exception as error:
        # log that
        counter = prom_endpoints_errors.labels(**labels)
        counter.inc()
        logger = logging.getLogger("requestsExceptions")
        logger.exception(f"`{request.method}` for `{request.url}`", exc_info=error)

    else:
        # do not log health check spam
        if not any(forbidden in request.url.path for forbidden in ["health_check", "metrics"]):
            process_time = round(time.time() - start_time, 2)

            # log that
            logger = logging.getLogger("requests")
            logger.info(f"`{request.method}` completed in `{process_time}` seconds for `{request.url}`")

        return response


# add routers
default_logger.debug("Registering Endpoints...")
for root, dirs, files in os.walk("Backend/endpoints"):
    for file in files:
        if file.endswith(".py") and not file.startswith("__init__"):
            file = file.removesuffix(".py")
            path = os.path.join(root, file).replace("/", ".").replace("\\", ".")
            resolved_path = importlib.util.resolve_name(path, None)

            module = importlib.import_module(resolved_path)
            router = setup = getattr(module, "router")
            app.include_router(router)
startup_progress.update(startup_task, advance=1)

# add exception handlers
default_logger.debug("Adding Exception Handlers...")
app.add_exception_handler(CustomException, handle_custom_exception)
for exc_class in bungio_errors.__dict__.values():
    try:
        if issubclass(exc_class, bungio_errors.HttpException):
            app.add_exception_handler(exc_class, handle_bungio_exception)
    except TypeError:
        pass
startup_progress.update(startup_task, advance=1)


@app.on_event("startup")
async def startup():
    # create the admin user for the website
    default_logger.debug("Setting Up Admin Account...")
    async with acquire_db_session() as db:
        await backend_user.create_admin(db=db)
    startup_progress.update(startup_task, advance=1)

    # register bungio
    get_bungio_client()
    startup_progress.update(startup_task, advance=1)

    # Update the Destiny 2 manifest
    default_logger.debug("Updating and Caching Destiny 2 Manifest...")
    await destiny_manifest.reset(soft=get_setting("ENABLE_DEBUG_MODE"))
    startup_progress.update(startup_task, advance=1)

    # register background events
    default_logger.debug("Loading Background Events...")
    events_loaded = register_background_events()
    default_logger.debug(f"< {events_loaded} > Background Events Loaded")
    startup_progress.update(startup_task, advance=1)

    # collect prometheus stats
    scheduler.add_job(
        func=collect_prometheus_stats,
        trigger="interval",
        seconds=60,
    )
    prom_endpoints_registered.set(len(app.router.routes))

    startup_progress.stop()
