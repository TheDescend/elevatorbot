from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.destiny.activities import DestinyActivities
from Backend.core.destiny.profile import DestinyProfile
from Backend.core.destiny.roles import UserRoles
from Backend.crud import discord_users, roles
from Backend.database.models import Roles
from Backend.dependencies import get_db_session
from NetworkingSchemas.basic import EmptyResponseModel
from NetworkingSchemas.destiny.roles import (
    EarnedRoleModel,
    EarnedRolesModel,
    MissingRolesModel,
    RequirementActivityModel,
    RoleDataModel,
    RoleModel,
    RolesModel,
    TimePeriodModel,
)

router = APIRouter(
    prefix="/destiny/{guild_id}/roles",
    tags=["destiny", "roles"],
)


@router.get("/get/all", response_model=RolesModel)
async def get_all(guild_id: int, db: AsyncSession = Depends(get_db_session)):
    """Get all roles for the corresponding guild"""

    result = []

    all_roles: list[Roles] = await roles.get_guild_roles(db=db, guild_id=guild_id)

    for role in all_roles:
        activity_models = []
        for activity_model in role.role_data.pop("require_activity_completions"):
            allowed_times = []
            disallowed_times = []

            for allowed_time in activity_model.pop("allow_time_periods"):
                allowed_times.append(TimePeriodModel(**allowed_time))
            for disallowed_time in activity_model.pop("disallow_time_periods"):
                disallowed_times.append(TimePeriodModel(**disallowed_time))

            activity_models.append(
                RequirementActivityModel(
                    allow_time_periods=allowed_times, disallow_time_periods=disallowed_times, **activity_model
                )
            )

        result.append(
            RoleModel(
                role_id=role.role_id,
                guild_id=role.guild_id,
                role_name=role.role_name,
                role_data=RoleDataModel(require_activity_completions=activity_models, **role.role_data),
            )
        )

    return RolesModel(roles=result)


@router.get("/get/all/{discord_id}", response_model=EarnedRolesModel)
async def get_user_all(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Get all roles for a user in their guild"""

    user = await discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)
    user_roles = UserRoles(db=db, user=profile)

    # update the users db entries
    activities = DestinyActivities(db=db, user=user)
    await activities.update_activity_db()

    return await user_roles.get_guild_roles(guild_id=guild_id)


@router.get("/get/missing/{discord_id}", response_model=MissingRolesModel)
async def get_user_missing(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Get the missing roles for a user in a guild"""

    user = await discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)
    user_roles = UserRoles(db=db, user=profile)

    # update the users db entries
    activities = DestinyActivities(db=db, user=user)
    await activities.update_activity_db()

    return await user_roles.get_missing_roles(guild_id=guild_id)


@router.get("/get/{role_id}/{discord_id}", response_model=EarnedRoleModel)
async def get_user_role(guild_id: int, role_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Get completion info for a role for a user"""

    user = await discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)
    user_roles = UserRoles(db=db, user=profile)

    sought_role = await roles.get_role(db=db, role_id=role_id)

    # update the users db entries
    activities = DestinyActivities(db=db, user=user)
    await activities.update_activity_db()

    return await user_roles.has_role(role=sought_role)


@router.post("/create", response_model=EmptyResponseModel)
async def create_role(guild_id: int, role: RoleModel, db: AsyncSession = Depends(get_db_session)):
    """Create a role. Note: role_id should be the discord role id"""

    await roles.create_role(db=db, role=role)


@router.post("/update/{role_id}", response_model=EmptyResponseModel)
async def update_role(guild_id: int, role: RoleModel, db: AsyncSession = Depends(get_db_session)):
    """Update a role by id"""

    await roles.update_role(db=db, role=role)


@router.delete("/delete/all", response_model=EmptyResponseModel)
async def delete_all(guild_id: int, db: AsyncSession = Depends(get_db_session)):
    """Delete all roles for a guild. Happens when Elevator gets removed from a guild f.e."""

    await roles.delete_guild_roles(db=db, guild_id=guild_id)


@router.delete("/delete/{role_id}", response_model=EmptyResponseModel)
async def delete_role(guild_id: int, role_id: int, db: AsyncSession = Depends(get_db_session)):
    """Delete a role from a guild"""

    await roles.delete_role(db=db, role_id=role_id)
