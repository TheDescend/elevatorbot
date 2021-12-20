import importlib.util
import logging
import os
import time

from fastapi import Depends, FastAPI, Request

from Backend.core.errors import CustomException, handle_custom_exception
from Backend.crud import backend_user
from Backend.database.base import get_async_session, setup_engine
from Backend.database.models import BackendUser, create_tables
from Backend.dependencies import (
    auth_get_user_with_read_perm,
    auth_get_user_with_write_perm,
)
from Backend.misc.initBackgroundEvents import register_background_events
from Backend.misc.initLogging import init_logging
from NetworkingSchemas.misc.auth import BackendUserModel

app = FastAPI()

# init logging
init_logging()
logger = logging.getLogger("requests")


# add middleware which logs every request
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # calculate the time needed to handle the request
    start_time = time.time()
    response = await call_next(request)
    process_time = round(time.time() - start_time, 2)

    # log that
    logger.info(
        "'%s' completed in '%s' seconds for '%s'",
        request.method,
        process_time,
        request.url,
    )

    return response


# add routers
for root, dirs, files in os.walk("Backend/endpoints"):
    for file in files:
        if file.endswith(f".py") and not file.startswith("__init__"):
            file = file.removesuffix(f".py")
            path = os.path.join(root, file).replace("/", ".").replace("\\", ".")
            resolved_path = importlib.util.resolve_name(path, None)

            module = importlib.import_module(resolved_path)
            router = setup = getattr(module, "router")
            app.include_router(router)


# add exception handlers
app.add_exception_handler(CustomException, handle_custom_exception)


# only allow people with read permissions
@app.get("/read_perm", response_model=BackendUserModel)
async def read_perm(user: BackendUser = Depends(auth_get_user_with_read_perm)):
    return BackendUserModel.from_orm(user)


# only allow people with write permissions
@app.get("/write_perm", response_model=BackendUserModel)
async def write_perm(user: BackendUser = Depends(auth_get_user_with_write_perm)):
    return BackendUserModel.from_orm(user)


@app.on_event("startup")
async def startup():
    # insert db tables
    print("Creating Database Tables...")
    await create_tables(engine=setup_engine())

    # create the admin user for the website
    print("Setting Up Admin Account...")
    async with get_async_session().begin() as db:
        await backend_user.create_admin(db=db)

    # register background events
    print("Loading Background Events...")
    events_loaded = register_background_events()
    print(f"< {events_loaded} > Background Events Loaded")
