from dis_snek.client import Snake

from ElevatorBot.backendNetworking.destiny.activities import DestinyActivities
from ElevatorBot.backendNetworking.destiny.weapons import DestinyWeapons
from ElevatorBot.commandHelpers.autocomplete import (
    DestinyActivityModel,
    DestinyWeaponModel,
    activities,
    activities_by_id,
    weapons,
    weapons_by_id,
)

# todo redo those on manifest update


async def load_autocomplete_options(client: Snake):
    """Fetch the needed data from the DB"""

    # get activities
    # loop through them all and add them to the global activities dict
    db_activities = await DestinyActivities(discord_member=None, client=None, discord_guild=None).get_all()
    for activity in db_activities.result["activities"]:
        model = DestinyActivityModel(
            name=activity["name"],
            description=activity["description"],
            activity_ids=activity["activity_ids"],
        )
        activities.update({model.name.lower(): model})
        for activity_id in model.activity_ids:
            activities_by_id.update({activity_id: model})

    # get weapons
    db_weapons = await DestinyWeapons(discord_member=None, client=None, discord_guild=None).get_all()
    for weapon in db_weapons.result["weapons"]:
        model = DestinyWeaponModel(
            name=weapon["name"],
            description=weapon["description"],
            flavor_text=weapon["flavor_text"],
            weapon_type=weapon["weapon_type"],
            weapon_slot=weapon["weapon_slot"],
            damage_type=weapon["damage_type"],
            ammo_type=weapon["ammo_type"],
            reference_ids=weapon["reference_ids"],
        )
        weapons.update({model.name.lower(): model})
        for reference_id in model.reference_ids:
            weapons_by_id.update({reference_id: model})
