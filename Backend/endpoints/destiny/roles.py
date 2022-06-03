from fastapi import APIRouter

from Backend.core.destiny.activities import DestinyActivities
from Backend.core.destiny.profile import DestinyProfile
from Backend.core.destiny.roles import UserRoles
from Backend.crud import crud_roles, discord_users
from Backend.database import acquire_db_session
from Shared.networkingSchemas import EmptyResponseModel
from Shared.networkingSchemas.destiny.roles import (
    EarnedRoleModel,
    EarnedRolesModel,
    MissingRolesModel,
    RoleModel,
    RolesModel,
)

router = APIRouter(
    prefix="/destiny/roles/{guild_id}",
    tags=["destiny", "roles"],
)


@router.get("/get/all", response_model=RolesModel)  # has test
async def get_all(guild_id: int):
    """Get all roles for the corresponding guild"""

    async with acquire_db_session() as db:
        return RolesModel(
            roles=[
                RoleModel.from_sql_model(role) for role in await crud_roles.get_guild_roles(db=db, guild_id=guild_id)
            ]
        )


@router.get("/{discord_id}/get/all", response_model=EarnedRolesModel)  # has test
async def get_user_all(guild_id: int, discord_id: int):
    """Get all roles for a user in their guild"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)
        user_roles = UserRoles(user=profile)

        # update the user's db entries
        activities = DestinyActivities(db=db, user=user)
        await activities.update_activity_db()

        return await user_roles.get_guild_roles(guild_id=guild_id)


@router.get("/{discord_id}/get/missing", response_model=MissingRolesModel)  # has test
async def get_user_missing(guild_id: int, discord_id: int):
    """Get the missing roles for a user in a guild"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)
        user_roles = UserRoles(user=profile)

        # update the user's db entries
        activities = DestinyActivities(db=db, user=user)
        await activities.update_activity_db()

        return await user_roles.get_missing_roles(guild_id=guild_id, db=db)


@router.get("/{discord_id}/get/{role_id}", response_model=EarnedRoleModel)  # has test
async def get_user_role(guild_id: int, role_id: int, discord_id: int):
    """Get completion info for a role for a user"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)
        user_roles = UserRoles(user=profile)

        sought_role = await crud_roles.get_role(db=db, role_id=role_id)

        # update the user's db entries
        activities = DestinyActivities(db=db, user=user)
        await activities.update_activity_db()

        return await user_roles.has_role(role=sought_role)


@router.post("/create", response_model=EmptyResponseModel)  # has test
async def create_role(guild_id: int, role: RoleModel):
    """Create a role"""

    async with acquire_db_session() as db:
        await crud_roles.create_role(db=db, role=role)


@router.post("/update/{role_id}", response_model=EmptyResponseModel)  # has test
async def update_role(guild_id: int, role_id: int, role: RoleModel):
    """Update a role by (old) id"""

    async with acquire_db_session() as db:
        await crud_roles.update_role(db=db, role=role, role_id=role_id)


@router.delete("/delete/all", response_model=EmptyResponseModel)  # has test
async def delete_all(guild_id: int):
    """Delete all roles for a guild. Happens when Elevator gets removed from a guild f.e."""

    async with acquire_db_session() as db:
        await crud_roles.delete_guild_roles(db=db, guild_id=guild_id)


@router.delete("/delete/{role_id}", response_model=EmptyResponseModel)  # has test
async def delete_role(guild_id: int, role_id: int):
    """Delete a role from a guild"""

    async with acquire_db_session() as db:
        await crud_roles.delete_role(db=db, role_id=role_id)
