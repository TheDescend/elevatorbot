import asyncio
import logging
from datetime import timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.destiny.activities import update_activities_in_background
from Backend.core.security.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from Backend.crud import backend_user, discord_users
from Backend.dependencies import get_db_session
from Backend.networking.bungieAuth import BungieRegistration
from Backend.networking.elevatorApi import ElevatorApi
from NetworkingSchemas.misc.auth import (
    BungieRegistrationInput,
    BungieTokenOutput,
    Token,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/bungie", response_model=BungieTokenOutput)  # has test
async def save_bungie_token(
    bungie_input: BungieRegistrationInput, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db_session)
):
    """Saves a bungie token"""

    # since this is a prerequisite for everything really, the test for this is called in insert_dummy_data()
    # it is not tested directly, since we don't want to update the activities in the background

    # get the initial token from the authentication
    auth = BungieRegistration()
    bungie_token = await auth.get_first_token(user_input=bungie_input)

    # save in db
    result, user, discord_id, guild_id = await discord_users.insert_profile(db=db, bungie_token=bungie_token)

    logger = logging.getLogger("registration")
    logger.info(
        "User with discord ID '%s' has registered successfully with destiny ID '%s', system '%s', and bungie name '%s'",
        user.discord_id,
        user.destiny_id,
        user.system,
        user.bungie_name,
    )

    # get users activities in background
    background_tasks.add_task(update_activities_in_background, user)

    # send a msg to Elevator and get the mutual guild ids
    elevator_api = ElevatorApi()
    response = await elevator_api.post(
        route_addition="registration/",
        json={
            "discord_id": discord_id,
        },
    )

    # see if we could connect
    if response is not None:
        # assign the role in all guilds
        await discord_users.add_registration_roles(
            db=db, discord_id=discord_id, guild_ids=response.content["guild_ids"]
        )

    return result


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session),
):
    """Generate and return a token"""

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
