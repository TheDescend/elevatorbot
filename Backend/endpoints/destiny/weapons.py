from bungio.models import DamageType, DestinyItemSubType
from fastapi import APIRouter

from Backend.bungio.manifest import destiny_manifest
from Backend.core.destiny.activities import DestinyActivities
from Backend.core.destiny.weapons import DestinyWeapons
from Backend.crud import discord_users
from Backend.database import acquire_db_session
from Shared.enums.destiny import DestinyWeaponSlotEnum
from Shared.networkingSchemas import DestinyWeaponModel
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

    weapons = await destiny_manifest.get_all_weapons()

    # loop through the weapons and format them
    format_helper = {}
    for weapon in weapons.values():
        if weapon.display_properties.name not in format_helper:
            format_helper.update(
                {
                    weapon.display_properties.name: DestinyWeaponModel(
                        name=weapon.display_properties.name,
                        description=weapon.display_properties.description,
                        flavor_text=weapon.flavor_text,
                        weapon_type=weapon.item_sub_type.display_name,
                        weapon_slot=DestinyWeaponSlotEnum(weapon.inventory.bucket_type_hash).display_name,
                        damage_type=weapon.default_damage_type.display_name,
                        ammo_type=weapon.equipping_block.ammo_type.display_name,
                        reference_ids=[weapon.hash],
                    )
                }
            )
        else:
            format_helper[weapon.display_properties.name].reference_ids.append(weapon.hash)

    return DestinyWeaponsModel(weapons=list(format_helper.values()))


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
            weapon_type=DestinyItemSubType(input_model.weapon_type) if input_model.weapon_type else None,
            damage_type=DamageType(input_model.damage_type) if input_model.damage_type else None,
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
