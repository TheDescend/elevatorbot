import logging
from datetime import timedelta

from bungio.error import BungieException, HttpException, NotFound
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from Backend.bungio.client import get_bungio_client
from Backend.core.destiny.activities import update_activities_in_background
from Backend.core.errors import CustomException
from Backend.core.security.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from Backend.crud import backend_user, discord_users
from Backend.database import acquire_db_session
from Backend.networking.elevatorApi import ElevatorApi
from Shared.networkingSchemas.misc.auth import BungieRegistrationInput, BungieTokenOutput, Token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/bungie", response_model=BungieTokenOutput)  # has test
async def save_bungie_token(bungie_input: BungieRegistrationInput, background_tasks: BackgroundTasks):
    """Saves a bungie token"""

    try:
        async with acquire_db_session() as db:
            user = None

            # since this is a prerequisite for everything really, the test for this is called in insert_dummy_data()
            # it is not tested directly, since we don't want to update the activities in the background

            # get the initial token from the authentication

            auth = await get_bungio_client().generate_auth(code=bungie_input.code)

            # save in db
            result, user, discord_id, guild_id = await discord_users.insert_profile(
                db=db, auth=auth, state=bungie_input.state
            )

            logger = logging.getLogger("registration")
            logger.info(
                f"User with discord ID `{user.discord_id}` has registered successfully with destiny ID `{user.destiny_id}`, system `{user.system}`, and bungie name `{user.bungie_name}`"
            )
    except Exception as error:
        # catch bungie errors, no need to log them
        if isinstance(error, CustomException) or isinstance(error, HttpException):
            raise error

        logger = logging.getLogger("registration")
        logger.exception(
            f"Registration for ID `{user.destiny_id if user else bungie_input.state}` failed", exc_info=error
        )
        raise error

    # get users activities in background
    background_tasks.add_task(update_activities_in_background, user)

    # send a msg to Elevator and get the mutual guild ids
    elevator_api = ElevatorApi()

    try:
        response = await elevator_api.post(
            route="/registration",
            json={
                "discord_id": discord_id,
            },
        )
    except Exception as error:
        response = None

        # it is bad if this fails, since it disrupts the user flow
        logger = logging.getLogger("elevatorApiExceptions")
        logger.exception("Registration Error", exc_info=error)

    # see if we could connect
    if response is not None:
        # assign the role in all guilds
        async with acquire_db_session() as db:
            await discord_users.add_registration_roles(
                db=db, discord_id=discord_id, guild_ids=response.content["guild_ids"]
            )

    return result


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Generate and return a token"""

    async with acquire_db_session() as db:
        user = await backend_user.authenticate(db=db, user_name=form_data.username, password=form_data.password)

    # check if OK
    if user:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await create_access_token(data={"sub": user.user_name}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
