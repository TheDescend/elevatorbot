from fastapi import APIRouter

from Backend.core.destiny.activities import DestinyActivities
from Backend.core.destiny.weapons import DestinyWeapons
from Backend.crud import discord_users
from Backend.database import acquire_db_session
from Shared.enums.destiny import DestinyDamageTypeEnum, DestinyItemSubTypeEnum
from Shared.networkingSchemas.destiny import (
    DestinyTopWeaponsInputModel,
    DestinyTopWeaponsModel,
    DestinyWeaponsModel,
    DestinyWeaponStatsInputModel,
    DestinyWeaponStatsModel,
)

router = APIRouter(
    prefix="/destiny/weapons",
    tags=["destiny", "weapons"],
)


@router.get("/get/all", response_model=DestinyWeaponsModel)  # has test
async def get_all():
    """Return all weapons there currently are"""

    async with acquire_db_session() as db:
        weapons = DestinyWeapons(db=db, user=None)
        return await weapons.get_all_weapons()


@router.post("/{guild_id}/{discord_id}/top", response_model=DestinyTopWeaponsModel)  # has test
async def get_top(
    guild_id: int,
    discord_id: int,
    input_model: DestinyTopWeaponsInputModel,
):
    """Get the users top weapons"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)

        # update the user's db entries
        activities = DestinyActivities(db=db, user=user)
        await activities.update_activity_db()

        weapons = DestinyWeapons(db=db, user=user)
        return await weapons.get_top_weapons(
            stat=input_model.stat,
            how_many_per_slot=input_model.how_many_per_slot,
            include_weapon_with_ids=input_model.include_weapon_with_ids,
            weapon_type=DestinyItemSubTypeEnum(input_model.weapon_type) if input_model.weapon_type else None,
            damage_type=DestinyDamageTypeEnum(input_model.damage_type) if input_model.damage_type else None,
            character_class=input_model.character_class,
            character_ids=input_model.character_ids,
            mode=input_model.mode,
            activity_hashes=input_model.activity_hashes,
            start_time=input_model.start_time,
            end_time=input_model.end_time,
        )


@router.post("/{guild_id}/{discord_id}/weapon", response_model=DestinyWeaponStatsModel)  # has test
async def get_weapon(
    guild_id: int,
    discord_id: int,
    input_model: DestinyWeaponStatsInputModel,
):
    """Get the users stats for the specified weapon"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)

        # update the user's db entries
        activities = DestinyActivities(db=db, user=user)
        await activities.update_activity_db()

        weapons = DestinyWeapons(db=db, user=user)
        return await weapons.get_weapon_stats(
            weapon_ids=input_model.weapon_ids,
            character_class=input_model.character_class,
            character_ids=input_model.character_ids,
            mode=input_model.mode,
            activity_hashes=input_model.activity_hashes,
            start_time=input_model.start_time,
            end_time=input_model.end_time,
        )
