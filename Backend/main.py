import logging
import time

from fastapi import Depends, FastAPI, Request

from Backend.core.errors import CustomException, handle_custom_exception
from Backend.database.base import setup_engine
from Backend.database.models import BackendUser, create_tables
from Backend.dependencies import (
    auth_get_user_with_read_perm,
    auth_get_user_with_write_perm,
)
from Backend.endpoints import auth
from Backend.endpoints.destiny import (
    account,
    activities,
    clan,
    lfg,
    profile,
    roles,
    steamPlayers,
    weapons,
)
from Backend.endpoints.misc import elevatorInfo, persistentMessages, polls
from Backend.misc.initBackgroundEvents import register_background_events
from Backend.misc.initLogging import init_logging
from Backend.schemas.misc.auth import BackendUserModel

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
app.include_router(elevatorInfo.router)
app.include_router(auth.router)
app.include_router(persistentMessages.router)
app.include_router(polls.router)
app.include_router(profile.router)
app.include_router(account.router)
app.include_router(clan.router)
app.include_router(lfg.router)
app.include_router(roles.router)
app.include_router(activities.router)
app.include_router(steamPlayers.router)
app.include_router(weapons.router)


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
    print ("Creating Database Tables...")
    await create_tables(engine=setup_engine())

    # insert db tables
    print ("Loading Background Events...")
    events_loaded = register_background_events(client)
    print (f"< {events_loaded} > Background Events Loaded")
