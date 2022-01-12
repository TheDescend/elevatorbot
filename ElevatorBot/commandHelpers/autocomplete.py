from dis_snek.models import AutocompleteContext
from rapidfuzz import fuzz, process

from Shared.NetworkingSchemas.destiny import DestinyActivityModel, DestinyLoreModel, DestinyWeaponModel

# all activities are in here at runtime
activities_grandmaster: dict[str, DestinyActivityModel] = {}
activities: dict[str, DestinyActivityModel] = {}
activities_by_id: dict[int, DestinyActivityModel] = {}

# all weapons are in here at runtime
weapons: dict[str, DestinyWeaponModel] = {}
weapons_by_id: dict[int, DestinyWeaponModel] = {}

# all lore is in here at runtime
lore: dict[str, DestinyLoreModel] = {}
lore_by_id: dict[int, DestinyLoreModel] = {}


async def autocomplete_send_activity_name(ctx: AutocompleteContext, activity: str):
    """Send the user the best fitting activities (fuzzy)"""

    best_matches = process.extract(activity.lower(), list(activities), scorer=fuzz.WRatio, limit=25)
    await ctx.send(
        choices=[
            {
                "name": activities[match[0]].name,
                "value": activities[match[0]].name.lower(),
            }
            for match in best_matches
        ]
    )


async def autocomplete_send_weapon_name(ctx: AutocompleteContext, weapon: str):
    """Send the user the best fitting weapons (fuzzy)"""

    best_matches = process.extract(weapon.lower(), list(weapons), scorer=fuzz.WRatio, limit=25)
    await ctx.send(
        choices=[
            {
                "name": weapons[match[0]].name,
                "value": weapons[match[0]].name.lower(),
            }
            for match in best_matches
        ]
    )


async def autocomplete_send_lore_name(ctx: AutocompleteContext, name: str):
    """Send the user the best fitting lore name (fuzzy)"""

    best_matches = process.extract(name.lower(), list(lore), scorer=fuzz.WRatio, limit=25)
    await ctx.send(
        choices=[
            {
                "name": lore[match[0]].name,
                "value": lore[match[0]].name.lower(),
            }
            for match in best_matches
        ]
    )
