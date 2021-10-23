import asyncio
from datetime import timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from Backend import crud
from Backend.core.destiny.activities import DestinyActivities
from Backend.core.errors import CustomException
from Backend.core.security.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_password_hash,
)
from Backend.database.models import BackendUser
from Backend.dependencies import get_db_session
from Backend.networking.elevatorApi import ElevatorApi
from Backend.schemas.misc.auth import (
    BackendUserModel,
    BungieTokenInput,
    BungieTokenOutput,
    Token,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/bungie", response_model=BungieTokenOutput)
async def save_bungie_token(bungie_token: BungieTokenInput, db: AsyncSession = Depends(get_db_session)):
    """Saves a bungie token"""

    # save in db
    result, user, discord_id, guild_id = await crud.discord_users.insert_profile(
        db=db,
        bungie_token=bungie_token,
    )

    if result.success:
        # get users activities in background
        activities = DestinyActivities(db=db, user=user)
        asyncio.create_task(activities.update_activity_db())

        # send a msg to Elevator and get the mutual guild ids
        elevator_api = ElevatorApi()
        response = await elevator_api.post(
            route_addition="registration/",
            json={
                "discord_id": discord_id,
            },
        )

        # loop through guilds
        data = []
        role_data = await crud.roles.get_registration_roles(db=db)
        for guild_id, guild_data in role_data.items():
            # make sure we are in that guild
            if guild_id in response.content["guild_ids"]:
                registered_role_id, unregistered_role_id = None, None

                # get both role ids
                for role in role_data:
                    if role.role_name == "Registered":
                        registered_role_id = role.role_id
                    elif role.role_name == "Unregistered":
                        unregistered_role_id = role.role_id

                # append that to the data we're gonna send elevator
                if registered_role_id or unregistered_role_id:
                    data.append(
                        {
                            "discord_id": discord_id,
                            "guild_id": guild_id,
                            "to_assign_role_ids": [registered_role_id] if registered_role_id else None,
                            "to_remove_role_ids": [unregistered_role_id] if unregistered_role_id else None,
                        }
                    )

        # send elevator that data to apply the roles
        if data:
            await elevator_api.post(
                route_addition="roles/",
                json={
                    "data": data,
                },
            )

    return result


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session),
):
    """Generate and return a token"""

    user = await crud.backend_user.authenticate(db=db, user_name=form_data.username, password=form_data.password)

    # check if OK
    if user:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.user_name}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/registration")
async def register(
    user_name: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db_session),
):
    """Register a new user"""

    # look if a user with that name exists
    user = await crud.backend_user._get_with_key(db, user_name)
    if user:
        raise HTTPException(
            status_code=400,
            detail="An account with this user name already exists",
        )

    hashed_password = get_password_hash(password)

    # todo dont make everyone admin
    # insert to db
    new_user = BackendUser(
        user_name=user_name,
        hashed_password=hashed_password,
        allowed_scopes=[],
        has_write_permission=True,
        has_read_permission=True,
    )
    await crud.backend_user._insert(db, new_user)

    # todo remove. just demonstration
    if new_user.user_name == "a":
        raise CustomException("wrongPw")

    return BackendUserModel.from_orm(new_user)
