import importlib.util
import logging
import os
import time
import traceback

from fastapi import Depends, FastAPI, Request

from Backend.core.destiny.manifest import DestinyManifest
from Backend.core.errors import CustomException, handle_custom_exception
from Backend.crud import backend_user
from Backend.database.base import get_async_sessionmaker, setup_engine
from Backend.database.models import BackendUser, create_tables
from Backend.dependencies import auth_get_user_with_read_perm, auth_get_user_with_write_perm
from Backend.misc.initBackgroundEvents import register_background_events
from Backend.misc.initLogging import init_logging
from Shared.functions.readSettingsFile import get_setting
from Shared.networkingSchemas.misc.auth import BackendUserModel

app = FastAPI()


# init logging
init_logging()

try:
    # install uvloop for faster asyncio (docker only)
    import uvloop

    print("Installing uvloop...")
    uvloop.install()
except ModuleNotFoundError:
    print("Uvloop not installed, skipping")


# only allow people with read permissions
@app.get("/read_perm", response_model=BackendUserModel)
async def read_perm(user: BackendUser = Depends(auth_get_user_with_read_perm)):
    return BackendUserModel.from_orm(user)


# only allow people with write permissions
@app.get("/write_perm", response_model=BackendUserModel)
async def write_perm(user: BackendUser = Depends(auth_get_user_with_write_perm)):
    return BackendUserModel.from_orm(user)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware which logs every request"""

    # calculate the time needed to handle the request
    start_time = time.time()
    try:
        response = await call_next(request)

    except Exception as error:
        # log that
        print(error)
        logger = logging.getLogger("requestsExceptions")
        logger.exception(
            f"""'{request.method}' for '{request.url}' - Error '{error}' - Traceback: \n'{"".join(traceback.format_tb(error.__traceback__))}'"""
        )
        raise error

    else:
        process_time = round(time.time() - start_time, 2)

        # log that
        logger = logging.getLogger("requests")
        logger.info(f"'{request.method}' completed in '{process_time}' seconds for '{request.url}'")

        return response


if get_setting("ENABLE_DEBUG_MODE"):

    @app.middleware("http")
    async def performance_counter(request: Request, call_next):
        """Middleware which does performance testing"""

        # calculate the time needed to handle the request
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        print(f"Performance Counter: `{request.url}` took `{process_time}s`")

        return response


# add routers
for root, dirs, files in os.walk("Backend/endpoints"):
    for file in files:
        if file.endswith(".py") and not file.startswith("__init__"):
            file = file.removesuffix(".py")
            path = os.path.join(root, file).replace("/", ".").replace("\\", ".")
            resolved_path = importlib.util.resolve_name(path, None)

            module = importlib.import_module(resolved_path)
            router = setup = getattr(module, "router")
            app.include_router(router)

# add exception handlers
app.add_exception_handler(CustomException, handle_custom_exception)


@app.on_event("startup")
async def startup():
    # insert db tables
    print("Creating Database Tables...")
    await create_tables(engine=setup_engine())

    # create the admin user for the website
    print("Setting Up Admin Account...")
    async with get_async_sessionmaker().begin() as db:
        await backend_user.create_admin(db=db)

    # Update the Destiny 2 manifest
    print("Updating Destiny 2 Manifest...")
    async with get_async_sessionmaker().begin() as db:
        manifest = DestinyManifest(db=db)
        await manifest.update(post_elevator=False)

    # register background events
    print("Loading Background Events...")
    events_loaded = register_background_events()
    print(f"< {events_loaded} > Background Events Loaded")
